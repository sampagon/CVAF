import asyncio
from flask import Flask, request, jsonify
from tools.computer import ComputerTool, ToolError, ToolResult

app = Flask(__name__)

# Create an instance of the ComputerTool class
computer_tool = ComputerTool()

@app.route("/perform_action", methods=["POST"])
async def perform_action():
    data = request.json

    # Extracting parameters from the incoming request
    action = data.get("action")
    text = data.get("text")
    coordinate = data.get("coordinate")

    try:
        # Call the ComputerTool's __call__ method asynchronously
        result = await computer_tool(
            action=action,
            text=text,
            coordinate=coordinate,
        )

        # Returning the result as JSON
        return jsonify({
            "output": result.output,
            "error": result.error,
            "base64_image": result.base64_image,
        })

    except ToolError as e:
        return jsonify({"error": str(e)}), 400

# For development purposes, run the Flask app directly (in production use a WSGI server)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
