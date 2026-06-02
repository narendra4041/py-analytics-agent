from e2b_code_interpreter import Sandbox

with Sandbox.create("py-analytics-agent") as sandbox:
    result = sandbox.run_code("""
import pandas as pd

result = {
    "status": "ok",
    "pandas": pd.__version__
}

result
""")

    print(result.text)
    print(result.error)