"""CLI entry point for quizmd-web-client."""

from __future__ import annotations

import argparse
import webbrowser


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="quizmd-web",
        description="QuizMD Web Client — play quizzes in your browser",
    )
    parser.add_argument(
        "source",
        nargs="?",
        default=None,
        help=(
            "GitHub source: owner/repo, GitHub URL to a .quiz.md file, "
            "or owner/repo/blob/branch/path.quiz.md"
        ),
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8742,
        help="Port to run the server on (default: 8742)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Don't open the browser automatically",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )
    args = parser.parse_args(argv)

    from .app import create_app

    app = create_app(default_source=args.source)

    if not args.no_open:
        url = f"http://{args.host}:{args.port}"
        if args.source:
            from urllib.parse import quote
            url += f"?source={quote(args.source)}"
        webbrowser.open(url)

    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
