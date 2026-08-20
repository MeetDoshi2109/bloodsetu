import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search } from 'lucide-react'
import { Select } from '../ui/Input'
import Button from '../ui/Button'
import { GUJARAT_CITIES, GUJARAT_AREAS, ALL_BLOOD_GROUPS } from '../../data/gujarat'

const URGENCY_OPTS = ['Planned', 'Urgent', 'Critical']

export default function BloodSearchForm({ compact = false, initialValues = {} }) {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    blood_group: initialValues.blood_group || '',
    city:        initialValues.city        || '',
    area:        initialValues.area        || '',
    urgency:     initialValues.urgency     || 'Urgent',
  })

  const areas = form.city ? (GUJARAT_AREAS[form.city] || []) : []

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const handleCityChange = (city) => {
    const cityAreas = GUJARAT_AREAS[city] || []
    setForm(f => ({ ...f, city, area: cityAreas[0] || '' }))
  }

  const handleSubmit = e => {
    e.preventDefault()
    if (!form.blood_group || !form.city || !form.area) return
    navigate('/find-blood', { state: form })
  }

  return (
    <form
      onSubmit={handleSubmit}
      className={compact ? 'flex flex-wrap gap-3 items-end' : 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4'}
    >
      <Select
        label={compact ? undefined : 'Blood Group'}
        value={form.blood_group}
        onChange={e => set('blood_group', e.target.value)}
        required
      >
        <option value="">Blood Group</option>
        {ALL_BLOOD_GROUPS.map(g => <option key={g}>{g}</option>)}
      </Select>

      <Select
        label={compact ? undefined : 'City'}
        value={form.city}
        onChange={e => handleCityChange(e.target.value)}
        required
      >
        <option value="">Select City</option>
        {GUJARAT_CITIES.map(c => <option key={c}>{c}</option>)}
      </Select>

      <Select
        label={compact ? undefined : 'Area'}
        value={form.area}
        onChange={e => set('area', e.target.value)}
        required
        disabled={!areas.length}
      >
        <option value="">Select Area</option>
        {areas.map(a => <option key={a}>{a}</option>)}
      </Select>

      <Select
        label={compact ? undefined : 'Urgency'}
        value={form.urgency}
        onChange={e => set('urgency', e.target.value)}
      >
        {URGENCY_OPTS.map(u => <option key={u}>{u}</option>)}
      </Select>

      {!compact && (
        <div className="sm:col-span-2 lg:col-span-4">
          <Button type="submit" size="lg" fullWidth icon={<Search size={18} />}>
            Find Blood Now
          </Button>
        </div>
      )}
      {compact && (
        <Button type="submit" icon={<Search size={16} />}>Search</Button>
      )}
    </form>
  )
}
