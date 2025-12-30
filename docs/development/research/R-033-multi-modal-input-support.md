# R-033: Multi-Modal Input Support

## Executive Summary

This research analyses approaches for supporting multi-modal inputs (images, audio, video) in persona generation. Research sessions often include photos, recordings, and visual artefacts. Recommended approach: phased implementation starting with image captioning and audio transcription, leveraging existing multi-modal LLM capabilities.

---

## Research Context

| Attribute | Value |
|-----------|-------|
| **ID** | R-033 |
| **Category** | Advanced Data Sources |
| **Status** | Complete |
| **Priority** | P3 |
| **Informs** | Future multi-modal features |

---

## Problem Statement

Research sessions produce more than text:
- Photos of users, environments, and artefacts
- Audio recordings of interviews
- Video recordings of usability sessions
- Whiteboard sketches and diagrams
- Screenshots and screen recordings

Currently, this rich data must be manually transcribed or described before Persona can use it.

---

## State of the Art Analysis

### Multi-Modal Input Types

| Type | Data | Processing | Complexity |
|------|------|------------|------------|
| **Images** | Photos, screenshots | Vision models | Medium |
| **Audio** | Interviews, recordings | Speech-to-text | Medium |
| **Video** | Sessions, demos | Frame + audio | High |
| **Documents** | PDFs, scans | OCR + layout | Medium |
| **Diagrams** | Sketches, flowcharts | Vision + structure | High |

### Vision Model Integration

**Direct Vision (Claude, GPT-4V):**
```python
async def describe_image(image_path: Path) -> str:
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()

    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_data
                    }
                },
                {
                    "type": "text",
                    "text": "Describe this image in detail for persona generation. Focus on user characteristics, environment, and context clues."
                }
            ]
        }]
    )
    return response.content[0].text
```

**Local Vision (LLaVA, Bakllava):**
```python
async def describe_image_local(image_path: Path) -> str:
    # Using Ollama with vision model
    response = await ollama.generate(
        model="llava:13b",
        prompt="Describe this image for persona generation",
        images=[str(image_path)]
    )
    return response["response"]
```

### Audio Transcription

**Whisper (Local/API):**
```python
import whisper

def transcribe_audio(audio_path: Path) -> str:
    model = whisper.load_model("base")
    result = model.transcribe(str(audio_path))
    return result["text"]
```

**AssemblyAI (Cloud):**
```python
import assemblyai as aai

async def transcribe_audio_cloud(audio_path: Path) -> str:
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(str(audio_path))
    return transcript.text
```

### Document Processing

**PDF with Docling:**
```python
from docling.document_converter import DocumentConverter

def extract_pdf(pdf_path: Path) -> str:
    converter = DocumentConverter()
    result = converter.convert(str(pdf_path))
    return result.document.export_to_markdown()
```

### Video Processing

**Frame Extraction + Audio:**
```python
import cv2
from moviepy.editor import VideoFileClip

def process_video(video_path: Path) -> MultiModalContent:
    # Extract audio
    clip = VideoFileClip(str(video_path))
    audio_path = video_path.with_suffix(".wav")
    clip.audio.write_audiofile(str(audio_path))

    # Extract key frames
    cap = cv2.VideoCapture(str(video_path))
    frames = []
    frame_interval = int(cap.get(cv2.CAP_PROP_FPS) * 10)  # Every 10 seconds

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if cap.get(cv2.CAP_PROP_POS_FRAMES) % frame_interval == 0:
            frames.append(frame)

    return MultiModalContent(
        audio_path=audio_path,
        key_frames=frames
    )
```

---

## Processing Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                Multi-Modal Processing Pipeline               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Input Files                                                 │
│     │                                                        │
│     ├─ Images ──────▶ Vision Model ──────▶ Descriptions     │
│     │                                                        │
│     ├─ Audio ───────▶ Whisper ───────────▶ Transcripts      │
│     │                                                        │
│     ├─ Video ───────▶ Frame + Audio ─────▶ Combined         │
│     │                                                        │
│     ├─ PDF ─────────▶ Docling ───────────▶ Markdown         │
│     │                                                        │
│     └─ Text ────────────────────────────▶ Pass-through      │
│                                                              │
│                         │                                    │
│                         ▼                                    │
│              ┌───────────────────┐                          │
│              │    Aggregator     │                          │
│              │  (merge context)  │                          │
│              └───────────────────┘                          │
│                         │                                    │
│                         ▼                                    │
│              ┌───────────────────┐                          │
│              │ Persona Generator │                          │
│              └───────────────────┘                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Evaluation Matrix

| Input Type | Local Option | Cloud Option | Quality | Cost |
|------------|--------------|--------------|---------|------|
| Images | LLaVA | Claude/GPT-4V | ⚠️/✅ | Low/Med |
| Audio | Whisper | AssemblyAI | ✅ | Low/Med |
| Video | FFmpeg + above | Cloud services | ⚠️ | High |
| PDF | Docling | N/A | ✅ | Low |

---

## Recommended Approach

### Phase 1: Image Support
- Integrate vision models (Claude, GPT-4V)
- Add local option (LLaVA via Ollama)
- CLI: `persona generate --from data/ --include-images`

### Phase 2: Audio Support
- Integrate Whisper for transcription
- Add speaker diarisation
- CLI: `persona generate --from data/ --transcribe`

### Phase 3: Document Support
- Integrate Docling for PDFs
- OCR for scanned documents
- CLI: `persona generate --from data/ --extract-pdf`

### Phase 4: Video Support
- Key frame extraction
- Combined audio/visual analysis
- CLI: `persona generate --from video.mp4`

### CLI Interface

```bash
# Generate from mixed media folder
persona generate --from research-data/ --multi-modal

# Specific modalities
persona generate --from data/ \
  --include-images \
  --transcribe-audio \
  --extract-documents

# Process specific file
persona media describe photo.jpg
persona media transcribe interview.mp3
persona media extract document.pdf
```

### Configuration

```yaml
multi_modal:
  enabled: true

  images:
    enabled: true
    provider: anthropic  # anthropic, openai, ollama
    model: claude-sonnet-4-20250514

  audio:
    enabled: true
    transcription:
      model: whisper-base  # whisper-tiny, whisper-base, whisper-large
      language: auto
      diarisation: false

  documents:
    enabled: true
    ocr: auto  # auto, always, never
    preserve_layout: true

  video:
    enabled: false  # Experimental
    frame_interval: 10  # seconds
    max_frames: 20
```

---

## Privacy Considerations

Multi-modal data has higher privacy risks:
- Images may contain faces
- Audio contains voices
- Video combines both

**Mitigations:**
- Face detection and blurring option
- Voice anonymisation option
- Local processing preference
- Clear consent workflows

---

## References

1. [Claude Vision](https://docs.anthropic.com/en/docs/build-with-claude/vision)
2. [OpenAI Whisper](https://github.com/openai/whisper)
3. [Docling](https://github.com/DS4SD/docling)
4. [LLaVA](https://llava-vl.github.io/)

---

## Related Documentation

- [R-017: Remote Data Ingestion](R-017-remote-data-ingestion.md)
- [F-126: URL Data Ingestion](../roadmap/features/completed/F-126-url-data-ingestion.md)

---

**Status**: Complete
