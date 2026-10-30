import { useEffect, useState } from "react"
import './shared.css'

const frames = ['< ! >', '<   >']

export default function BlinkingError({ error }: { error: string }) {
  const [blinkIndex, setBlinkIndex] = useState(0)
  const [blinkFrame, setBlinkFrame] = useState(frames[0])

  useEffect(() => {
    setTimeout(() => {
      // increment the frame every 500ms (and looping when we reach the end with modulo)
      let newIndex = (blinkIndex + 1) % frames.length
      setBlinkIndex(newIndex)
      setBlinkFrame(frames[newIndex])
    }, 500)
  }, [blinkFrame])

  return (
    <div className="info-container">
      <pre className="info-anim" aria-hidden="true">{blinkFrame}</pre>
      <p className="info-text">{error.toLocaleLowerCase()}</p>
    </div>
  )
}