import os
import sys
import uvicorn

DEBUG = os.environ.get("DEBUG", "").strip().lower() in {"1", "true", "on", "yes"}


def main(argv=sys.argv[1:]):
    print(f"Running with DEBUG={DEBUG}")
    try:
        uvicorn.run("todo.server:app", host="0.0.0.0", port=3001, reload=DEBUG)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
