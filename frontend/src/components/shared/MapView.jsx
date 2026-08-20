import { MapContainer, TileLayer, Marker, Popup, CircleMarker } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Fix default Leaflet icon
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl:       'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl:     'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

const CITY_CENTERS = {
  Ahmedabad:  [23.0225, 72.5714],
  Vadodara:   [22.3072, 73.1812],
  Surat:      [21.1702, 72.8311],
  Rajkot:     [22.3039, 70.8022],
  Gandhinagar:[23.2156, 72.6369],
  Bhavnagar:  [21.7645, 72.1519],
  Jamnagar:   [22.4707, 70.0577],
  Anand:      [22.5645, 72.9289],
  Nadiad:     [22.6916, 72.8634],
  Mehsana:    [23.5880, 72.3693],
}

const hospitalIcon = L.divIcon({
  html: '<div style="background:#3b82f6;width:12px;height:12px;border-radius:50%;border:2px solid white;box-shadow:0 0 8px rgba(59,130,246,0.8)"></div>',
  className: '', iconSize: [12,12], iconAnchor: [6,6],
})
const bankIcon = L.divIcon({
  html: '<div style="background:#2ecc71;width:12px;height:12px;border-radius:50%;border:2px solid white;box-shadow:0 0 8px rgba(46,204,113,0.8)"></div>',
  className: '', iconSize: [12,12], iconAnchor: [6,6],
})
const campIcon = L.divIcon({
  html: '<div style="background:#f0c040;width:12px;height:12px;border-radius:50%;border:2px solid white;box-shadow:0 0 8px rgba(240,192,64,0.8)"></div>',
  className: '', iconSize: [12,12], iconAnchor: [6,6],
})

// Approximate area coords — uses city center with small offset per index
function getAreaCoords(city, area, index = 0) {
  const base = CITY_CENTERS[city] || [22.5, 72.5]
  const offsets = [
    [0,0],[0.01,0.01],[0.01,-0.01],[-0.01,0.01],[-0.01,-0.01],
    [0.02,0],[0,0.02],[-0.02,0],[0,-0.02],[0.02,0.02],
  ]
  const off = offsets[index % offsets.length]
  return [base[0] + off[0], base[1] + off[1]]
}

export default function MapView({ city = 'Vadodara', hospitals = [], banks = [], camps = [], donors = [], height = 400 }) {
  const center = CITY_CENTERS[city] || [22.5, 72.5]

  return (
    <div style={{ height }} className="rounded-2xl overflow-hidden border border-white/10">
      <MapContainer center={center} zoom={12} style={{ height: '100%', width: '100%' }}
        attributionControl={false}>
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://carto.com/">CARTO</a>'
        />

        {hospitals.map((h, i) => (
          <Marker key={`h-${h.id}`} position={getAreaCoords(city, h.area, i)} icon={hospitalIcon}>
            <Popup>
              <div className="text-sm">
                <p className="font-bold text-white">{h.name}</p>
                <p className="text-white/60 text-xs">{h.area}, {h.city}</p>
                {h.doctor_name && <p className="text-xs text-blue-300">Dr. {h.doctor_name}</p>}
                <p className="text-xs text-white/50 mt-1">{h.phone}</p>
              </div>
            </Popup>
          </Marker>
        ))}

        {banks.map((b, i) => (
          <Marker key={`b-${b.id}`} position={getAreaCoords(city, b.area, i + 5)} icon={bankIcon}>
            <Popup>
              <div className="text-sm">
                <p className="font-bold text-white">{b.name}</p>
                <p className="text-white/60 text-xs">{b.area}, {b.city}</p>
                <p className="text-xs text-white/50 mt-1">{b.phone}</p>
              </div>
            </Popup>
          </Marker>
        ))}

        {camps.map((c, i) => (
          <Marker key={`c-${c.id}`} position={getAreaCoords(city, c.area, i + 3)} icon={campIcon}>
            <Popup>
              <div className="text-sm">
                <p className="font-bold text-white">{c.organizer}</p>
                <p className="text-white/60 text-xs">{c.area}, {c.city}</p>
                <p className="text-xs text-yellow-300">{c.camp_date} · {c.timings}</p>
              </div>
            </Popup>
          </Marker>
        ))}

        {donors.map((d, i) => (
          <CircleMarker key={`d-${d.id}`} center={getAreaCoords(city, d.area, i + 7)} radius={8}
            pathOptions={{ color: '#e74c3c', fillColor: '#c0392b', fillOpacity: 0.8 }}>
            <Popup>
              <div className="text-sm">
                <p className="font-bold text-white">{d.name}</p>
                <p className="text-xs text-red-300">Blood Group: {d.blood_group}</p>
                <p className="text-white/60 text-xs">{d.area}</p>
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  )
}

export function MapLegend() {
  return (
    <div className="flex flex-wrap gap-4 mt-3 text-xs text-white/50">
      <span className="flex items-center gap-1.5">
        <span className="w-3 h-3 rounded-full bg-blue-500 inline-block" /> Hospital
      </span>
      <span className="flex items-center gap-1.5">
        <span className="w-3 h-3 rounded-full bg-emerald-500 inline-block" /> Blood Bank
      </span>
      <span className="flex items-center gap-1.5">
        <span className="w-3 h-3 rounded-full bg-yellow-400 inline-block" /> Blood Camp
      </span>
      <span className="flex items-center gap-1.5">
        <span className="w-3 h-3 rounded-full bg-blood-600 inline-block" /> Donor
      </span>
    </div>
  )
}
