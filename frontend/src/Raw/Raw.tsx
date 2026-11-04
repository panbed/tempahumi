import { useEffect, useState } from 'react'
import './Raw.css'

import type { ClimateInfoInterface } from '../Utils/ClimateInfo'

import TextSpinner from '../Utils/TextSpinner'
import BlinkingError from '../Utils/BlinkingError'

export default function Raw() {
  const [rawClimateData, setRawClimateData] = useState<ClimateInfoInterface[]>()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchRawClimateData() {
      try {
        setLoading(true)

        // fetch from backend, get JSON and set rawClimateData (we dont have a chart this time..)
        const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/climate-info/latest`)
        const responseData = await response.json()

        setRawClimateData(responseData)
        setLoading(false)
      }
      catch (error) {
        let message

        if (error instanceof Error) message = error.message
        else message = String(error)

        setError(message)
        setLoading(false)
      }
    }

    fetchRawClimateData()
  }, [])

  if (loading) {
    return (
      <div id='chart-loading'>
        <TextSpinner />
      </div>
    )
  }

  else if (error) {
    return (
      <div id='chart-error'>
        <BlinkingError error={error} />
      </div>
    )
  }

  return (
    <>
      <table>
        <caption>temperature and humidity</caption>
        <thead>
          <tr>
            <th scope='col'>timestamp</th>
            <th scope='col'>temperature</th>
            <th scope='col'>humidity</th>
          </tr>
        </thead>
        <tbody>
          {rawClimateData?.map((climate: ClimateInfoInterface) => 
            <tr>
              <th scope='row'>{climate['timestamp']}</th>
              <td>{climate['temperature']}</td>
              <td>{climate['humidity']}</td>
            </tr>
          )}
        </tbody>
      </table>
    </>
  )
}