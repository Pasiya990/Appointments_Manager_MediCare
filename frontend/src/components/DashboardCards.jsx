import { CalendarDays, CheckCircle2, CircleX, ListChecks, UsersRound } from 'lucide-react'

const cards = [
  { key: 'total', label: 'Total appointments', icon: ListChecks, tone: 'blue' },
  { key: 'scheduled', label: 'Scheduled', icon: CalendarDays, tone: 'teal' },
  { key: 'completed', label: 'Completed', icon: CheckCircle2, tone: 'green' },
  { key: 'cancelled', label: 'Cancelled', icon: CircleX, tone: 'rose' },
  { key: 'today', label: "Today's visits", icon: UsersRound, tone: 'violet' },
]
export default function DashboardCards({ stats }) {
  return <div className="stats-grid">{cards.map(({ key, label, icon: Icon, tone }) => <article className="stat-card" key={key}>
    <div className={`stat-icon ${tone}`}><Icon size={19} strokeWidth={1.8} /></div>
    <div><div className="stat-value">{stats?.[key] ?? '—'}</div><div className="stat-label">{label}</div></div>
  </article>)}</div>
}
