from flask import Flask, render_template, request, send_file, after_this_request, jsonify
from cryptography.fernet import Fernet
from database import db, FileLog
from dotenv import load_dotenv
import os
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Database config ---
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///local.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create tables on startup
with app.app_context():
    db.create_all()

# Load the Fernet key
with open("secret.key", "rb") as f:
    key = f.read()
fernet = Fernet(key)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/encrypt", methods=["POST"])
def encrypt():
    file = request.files["file"]
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        print("Encrypting:", filename)

        try:
            with open(file_path, "rb") as f:
                data = f.read()
            encrypted_data = fernet.encrypt(data)
        except Exception as e:
            print("Encryption error:", str(e))
            # ✅ Log failed attempt
            log = FileLog(filename=filename, action='encrypt',
                          file_size=file_size, ip_address=request.remote_addr, status='error')
            db.session.add(log)
            db.session.commit()
            return render_template("index.html", status="error")

        encrypted_name = "encrypted_" + filename
        encrypted_path = os.path.join(UPLOAD_FOLDER, encrypted_name)
        with open(encrypted_path, "wb") as f:
            f.write(encrypted_data)

        # ✅ Log successful encryption
        log = FileLog(filename=filename, action='encrypt',
                      file_size=file_size, ip_address=request.remote_addr, status='success')
        db.session.add(log)
        db.session.commit()

        @after_this_request
        def cleanup(response):
            try:
                os.remove(file_path)
                os.remove(encrypted_path)
                print("Encrypted file and uploaded file cleaned up.")
            except Exception as e:
                print("Cleanup error:", str(e))
            return response

        return send_file(encrypted_path, as_attachment=True, download_name=encrypted_name)

    return render_template("index.html", status="error")


@app.route("/decrypt", methods=["POST"])
def decrypt():
    file = request.files["file"]
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        print("Uploaded filename:", filename)

        try:
            with open(file_path, "rb") as f:
                encrypted_data = f.read()
            decrypted_data = fernet.decrypt(encrypted_data)
        except Exception as e:
            print("Decryption error:", str(e))
            # ✅ Log failed attempt
            log = FileLog(filename=filename, action='decrypt',
                          file_size=file_size, ip_address=request.remote_addr, status='error')
            db.session.add(log)
            db.session.commit()
            return render_template("index.html", status="error")

        original_name = filename.replace(".encrypted", "")
        decrypted_path = os.path.join(UPLOAD_FOLDER, "temp_" + original_name)
        with open(decrypted_path, "wb") as f:
            f.write(decrypted_data)

        # ✅ Log successful decryption
        log = FileLog(filename=filename, action='decrypt',
                      file_size=file_size, ip_address=request.remote_addr, status='success')
        db.session.add(log)
        db.session.commit()

        @after_this_request
        def cleanup(response):
            try:
                os.remove(file_path)
                os.remove(decrypted_path)
                print("Temporary files cleaned up.")
            except Exception as e:
                print("Error cleaning up:", str(e))
            return response

        return send_file(decrypted_path, as_attachment=True, download_name=original_name)

    return render_template("index.html", status="error")


@app.route("/history")
def history():
    logs = FileLog.query.order_by(FileLog.created_at.desc()).limit(50).all()
    return jsonify([log.to_dict() for log in logs])


if __name__ == "__main__":
    app.run(debug=True)