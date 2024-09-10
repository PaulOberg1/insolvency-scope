from flask import Flask, Blueprint, request, jsonify

bp = Blueprint("LogOutBP",__name__)

@bp.route("/logout", methods=["POST"])
def logout():
    try:
        return jsonify({"message":"success"})

    except Exception as e:
        return jsonify({"message":f"logout failed: {e}"})
    


