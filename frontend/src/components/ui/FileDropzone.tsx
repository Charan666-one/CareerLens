import { useCallback, useState } from "react"
import { useDropzone, type FileRejection } from "react-dropzone"

const MAX_SIZE = 5 * 1024 * 1024 // matches the backend's 5MB cap

// Mirrors backend/app/services/nlp/resume_parser.py's SUPPORTED_EXTENSIONS
const ACCEPT = {
  "application/pdf": [".pdf"],
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
  "text/plain": [".txt"],
}

interface FileDropzoneProps {
  onFile: (file: File) => void
  label: string
  disabled?: boolean
}

export default function FileDropzone({ onFile, label, disabled }: FileDropzoneProps) {
  const [rejection, setRejection] = useState<string | null>(null)

  const onDrop = useCallback(
    (accepted: File[], rejected: FileRejection[]) => {
      if (rejected.length > 0) {
        const err = rejected[0].errors[0]
        setRejection(
          err?.code === "file-too-large" ? "That file is over the 5 MB limit." : "Unsupported file type — use PDF, DOCX, or TXT."
        )
        return
      }
      setRejection(null)
      if (accepted[0]) onFile(accepted[0])
    },
    [onFile]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPT,
    maxSize: MAX_SIZE,
    multiple: false,
    disabled,
  })

  return (
    <div>
      <div
        {...getRootProps()}
        className={`border border-dashed rounded px-6 py-8 text-center cursor-pointer transition-colors ${
          isDragActive ? "border-brass bg-brass/5" : "border-stone-line"
        } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
      >
        <input {...getInputProps()} />
        <p className="text-sm text-text-dim">
          {label} — drag a file here or <span className="text-brass-strong underline">browse</span>
        </p>
        <p className="text-xs text-text-dim mt-1">PDF, DOCX, or TXT · up to 5 MB</p>
      </div>
      {rejection && <p className="text-warn text-xs mt-2">{rejection}</p>}
    </div>
  )
}
