import whisper
import ffmpeg
import os

def convert_to_wav(input_path, output_path):
    """
    Convert MP3 to WAV format using FFmpeg.
    """
    try:
        ffmpeg.input(input_path).output(output_path, format='wav', acodec='pcm_s16le', ac=1, ar='16000').run(quiet=True)
        print(f"Converted {input_path} to {output_path}")
    except ffmpeg.Error as e:
        print(f"Error during conversion: {e}")
        raise

def transcribe_audio(file_path):
    """
    Transcribe audio file to text using OpenAI Whisper.
    """
    # Load the Whisper model
    model = whisper.load_model("base")  # You can choose 'tiny', 'base', 'small', 'medium', or 'large'

    # Transcribe the audio file
    print("Transcribing...")
    result = model.transcribe(file_path)
    return result["text"]

def main():
    # Input MP3 file path
    input_mp3 = "your_audio_file.mp3"  # Replace with your MP3 file path
    output_wav = "converted_audio.wav"

    # Convert MP3 to WAV
    if not os.path.exists(input_mp3):
        print(f"File not found: {input_mp3}")
        return

    convert_to_wav(input_mp3, output_wav)

    # Transcribe the WAV file
    transcription = transcribe_audio(output_wav)
    print("\nTranscription:")
    print(transcription)

    # Clean up converted WAV file
    os.remove(output_wav)

if __name__ == "__main__":
    main()
