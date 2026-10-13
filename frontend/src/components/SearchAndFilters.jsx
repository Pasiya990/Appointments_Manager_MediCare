import { CalendarDays, Search, SlidersHorizontal, X } from 'lucide-react'

const doctors = ['Dr. Emily Carter', 'Dr. James Wilson', 'Dr. Sophia Anderson', 'Dr. Daniel Roberts', 'Dr. Olivia Martin']
const types = ['General Consultation', 'Follow-up', 'Dental Consultation', 'Specialist Consultation', 'Routine Check-up']
export default function SearchAndFilters({ filters, onChange, onClear }) {
  return <div className="filter-panel">
    <label className="search-box"><Search size={17} /><input aria-label="Search patient or doctor" placeholder="Search patient or doctor..." value={filters.search} onChange={(e) => onChange('search', e.target.value)} /></label>
    <div className="select-control"><SlidersHorizontal size={15} /><select aria-label="Filter by status" value={filters.status} onChange={(e) => onChange('status', e.target.value)}><option value="">All statuses</option>{['Scheduled', 'Completed', 'Cancelled'].map((x) => <option key={x}>{x}</option>)}</select></div>
    <div className="select-control"><select aria-label="Filter by doctor" value={filters.doctor} onChange={(e) => onChange('doctor', e.target.value)}><option value="">All doctors</option>{doctors.map((x) => <option key={x}>{x}</option>)}</select></div>
    <div className="select-control"><select aria-label="Filter by appointment type" value={filters.appointment_type} onChange={(e) => onChange('appointment_type', e.target.value)}><option value="">All types</option>{types.map((x) => <option key={x}>{x}</option>)}</select></div>
    <label className="date-control"><CalendarDays size={15} /><input aria-label="Filter by date" type="date" value={filters.date} onChange={(e) => onChange('date', e.target.value)} /></label>
    <button className="clear-button" onClick={onClear} title="Clear filters"><X size={16} /><span>Clear</span></button>
  </div>
}
