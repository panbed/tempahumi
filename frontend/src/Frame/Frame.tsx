import { Link, Outlet } from 'react-router'
import './Frame.css'

export default function Frame() {
  return (
    <>
      <nav id='navbar'>
        <ul>
          <li><Link to='/'>chart</Link></li>
          <li><Link to='/raw'>table</Link></li>
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