import { useEffect, useState } from 'react'
import './Chart.css'
import {
  CategoryScale,
  Chart as ChartJS,
  Decimation,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Title,
  Tooltip,
} from 'chart.js'

import TextSpinner from '../Utils/TextSpinner'
import BlinkingError from '../Utils/BlinkingError'
import { Line } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Decimation
)

export const options = {
  plugins: {
    animation: false,
    parsing: false,
    plugins: {
      decimation: {
        enabled: true,
        algorithm: 'lttb',
        samples: 1500
      }
    },
    responsive: true,
    interaction: {
      mode: 'x',
      intersect: false,
    },
    scales: {
      x: {
        type: 'time',
        time: {
          unit: 'hour',
          displayFormats: {
            hour: 'MMM dd, hh:mm a'
          }
        },
        title: {
          display: true,
          text: 'da time,'
        }
      },
      yTemp: {
        type: 'linear',
        display: true,
        position: 'left',
        title: {
          display: true,
          text: 'tempeatur (°F)'
        }
      },
      yHumidity: {
        type: 'linear',
        display: true,
        position: 'right',
        title: {
          display: true,
          text: 'hdumity (%)'
        },
        grid: {
          drawOnChartArea: false,
        }
      }
    }
  }
}

export default function Chart() {
  const [climateData, setClimateData] = useState([]) // json w/ climate data
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchClimateData() {
      try {
        setLoading(true)

        // fetch data from backend, get the JSON and then set climateData to the JSON
        const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/climate-info/latest`)
        const responseData = await response.json()
        

        // sort the climate data by timestamp so we dont get data that goes backwards in time
        responseData.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))

        console.log(responseData)

        const temperatureDataset = responseData.map(item => ({
          x: new Date(item.timestamp).valueOf(),
          y: item.temperature
        }))

        const humidityDataset = responseData.map(item => ({
          x: new Date(item.timestamp).valueOf(),
          y: item.humidity
        }))

        let data = {
          datasets: [
            {
              label: 'tempeatur (°F)',
              data: temperatureDataset,
              yAxisID: 'yTemp',
              tension: 0.4
            },
            {
              label: 'hdumity (%)',
              data: humidityDataset,
              yAxisID: 'yHumidity',
              tension: 0.4
            },
          ]
        }

        setClimateData(data)
        setLoading(false)
      }
      catch (error) {
        // interesting article i read about catching errors in typescript:
        // kentcdodds.com/blog/get-a-catch-block-error-message-with-typescript
        let message

        if (error instanceof Error) message = error.message
        else message = String(error)

        setError(message)
        setLoading(false)
      }
    }

    fetchClimateData()
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
      <div>
        <Line options={options} data={climateData}/>
      </div>
    </>
  )
}