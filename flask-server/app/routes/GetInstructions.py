from flask import Flask, jsonify, Blueprint
import json

# Define new Blueprint "GetInstructionsBP" to register in __init__.py
bp = Blueprint("GetInstructionsBP",__name__)

@bp.route("/getInstructions")
def getInstructions():
    """
    Route to fetch instructions from server-side storage.

    Returns:
        JSON response containing the instructions.
    """

    #Access instructions from redis object
    from .. import r
    instructionData = r.get("instructions")
    instructions = json.loads(instructionData)

    #Return instructions to the frontend
    return jsonify({"instructions":instructions})
