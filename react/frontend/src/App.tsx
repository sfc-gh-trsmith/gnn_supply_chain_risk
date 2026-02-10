import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Home } from './pages/Home'
import { Executive } from './pages/Executive'
import { Network } from './pages/Network'
import { Tier2Analysis } from './pages/Tier2Analysis'
import { Simulator } from './pages/Simulator'
import { Mitigation } from './pages/Mitigation'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="executive" element={<Executive />} />
          <Route path="network" element={<Network />} />
          <Route path="tier2" element={<Tier2Analysis />} />
          <Route path="simulator" element={<Simulator />} />
          <Route path="mitigation" element={<Mitigation />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
