import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Route, Routes } from 'react-router'
import './index.css'

import Chart from './Chart/Chart'
import Raw from './Raw/Raw'
import Frame from './Frame/Frame'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path='/' element={<Frame />}>
          <Route index element={<Chart />} />
          <Route path='raw' element={<Raw />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
