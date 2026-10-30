import { useEffect, useState } from "react"
import './shared.css'

const frames = ['|', '/', '-', '\\']

export default function TextSpinner() {
  const [loaderIndex, setLoaderIndex] = useState(0)
  const [loaderFrame, setLoaderFrame] = useState(frames[0])

  useEffect(() => {
    setTimeout(() => {
      // increment the frame every 250ms (and looping when we reach the end with modulo)
      let newIndex = (loaderIndex + 1) % frames.length
      setLoaderIndex(newIndex)
      setLoaderFrame(frames[newIndex])
    }, 250)
  }, [loaderFrame])

  return (
    <div aria-label="Loading chart..." className="info-container">
      <pre className="info-anim" aria-hidden="true">{loaderFrame}</pre>
    </div>
  )
}