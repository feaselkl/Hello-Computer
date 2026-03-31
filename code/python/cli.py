"""Command-line interface for Azure AI Speech demos."""
import argparse
import sys

from dotenv import load_dotenv


def cmd_stt(args: argparse.Namespace) -> None:
    from speech_lib import transcribe_from_microphone, transcribe_from_wav

    if args.file:
        print(f"Transcribing from {args.file} ...")
        text = transcribe_from_wav(args.file)
    else:
        print("Listening on your microphone (speak now) ...")
        text = transcribe_from_microphone()

    print(f"\nRecognized: {text}")


def cmd_tts(args: argparse.Namespace) -> None:
    from speech_lib import speak_text, synthesize_to_wav

    endpoint_id = args.endpoint_id  # None if not provided; env var checked in library

    if args.output:
        print(f"Synthesizing to {args.output} ...")
        synthesize_to_wav(
            args.text, args.output,
            voice_name=args.voice, endpoint_id=endpoint_id,
        )
        print(f"Saved to {args.output}")
    else:
        print("Speaking ...")
        speak_text(args.text, voice_name=args.voice, endpoint_id=endpoint_id)
        print("Done.")


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Azure AI Speech CLI demos"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # Speech-to-text
    stt = sub.add_parser("stt", help="Speech-to-text")
    stt.add_argument(
        "--file", "-f",
        help="Path to a .wav file (default: use microphone)",
    )

    # Text-to-speech
    tts = sub.add_parser("tts", help="Text-to-speech")
    tts.add_argument(
        "--text", "-t", required=True,
        help="Text to speak",
    )
    tts.add_argument(
        "--output", "-o",
        help="Save to .wav file instead of playing through speaker",
    )
    tts.add_argument(
        "--voice", "-v",
        default="en-US-JennyNeural",
        help="Voice name (default: en-US-JennyNeural)",
    )
    tts.add_argument(
        "--endpoint-id", "-e",
        help="Custom Neural Voice endpoint ID (or set AZURE_SPEECH_ENDPOINT_ID)",
    )

    args = parser.parse_args()

    try:
        if args.command == "stt":
            cmd_stt(args)
        elif args.command == "tts":
            cmd_tts(args)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
