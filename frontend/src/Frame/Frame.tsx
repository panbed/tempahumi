import { Outlet } from 'react-router'
import './Frame.css'

export default function Frame() {
  return (
    <>
      <nav id='navbar'>
        <ul>
          <li>chart</li>
          <li>table</li>
        </ul>
      </nav>
      <div id='frame'>

        <main id='content'>
          <Outlet />
        </main>
      </div>
    </>
  )
}