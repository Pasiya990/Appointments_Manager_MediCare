import { useCallback, useEffect, useState } from 'react'
import { Activity, Bell, CalendarPlus, ChevronDown, CircleHelp, HeartPulse, LayoutDashboard, Menu, RefreshCw, Settings } from 'lucide-react'
import DashboardCards from './components/DashboardCards.jsx'
import AppointmentTable from './components/AppointmentTable.jsx'
import AppointmentForm from './components/AppointmentForm.jsx'
import ConfirmDialog from './components/ConfirmDialog.jsx'
import SearchAndFilters from './components/SearchAndFilters.jsx'
import AuthScreen from './components/AuthScreen.jsx'
import { createAppointment, deleteAppointment, getAppointments, getStats, getCurrentUser, logout, updateAppointment } from './services/appointmentService.js'

export default function App() {
  const [user, setUser] = useState(null)
  const [authLoading, setAuthLoading] = useState(true)
  const [appointments, setAppointments] = useState([])
  const [stats, setStats] = useState(null)
  const [filters, setFilters] = useState({ search: '', status: '', doctor: '', appointment_type: '', date: '' })
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState('')
  const [notice, setNotice] = useState('')
  const [formAppointment, setFormAppointment] = useState(undefined)
  const [deleteAppointmentItem, setDeleteAppointmentItem] = useState(null)
  const [mobileNavOpen, setMobileNavOpen] = useState(false)

  useEffect(() => {
    getCurrentUser().then(setUser).catch(() => setUser(null)).finally(() => setAuthLoading(false))
  }, [])

  const refresh = useCallback(async () => {
    if (!user) return
    setLoading(true); setLoadError('')
    try {
      const [rows, summary] = await Promise.all([getAppointments(filters), getStats()])
      setAppointments(rows); setStats(summary)
    } catch (error) { setLoadError(error.message) }
    finally { setLoading(false) }
  }, [filters, user])
  useEffect(() => { if (!user) return undefined; const timer = setTimeout(refresh, 220); return () => clearTimeout(timer) }, [refresh, user])
  useEffect(() => { if (!notice) return undefined; const timer = setTimeout(() => setNotice(''), 3500); return () => clearTimeout(timer) }, [notice])
  function changeFilter(field, value) { setFilters((current) => ({ ...current, [field]: value })) }
  async function saveAppointment(data) {
    if (formAppointment) await updateAppointment(formAppointment.id, data)
    else await createAppointment(data)
    setFormAppointment(undefined); setNotice(formAppointment ? 'Appointment updated successfully.' : 'Appointment created successfully.'); await refresh()
  }
  async function removeAppointment() {
    await deleteAppointment(deleteAppointmentItem.id); setDeleteAppointmentItem(null); setNotice('Appointment deleted.'); await refresh()
  }
  async function signOut() {
    try { await logout() } finally { setUser(null); setAppointments([]); setStats(null) }
  }
  const dateLabel = new Intl.DateTimeFormat(undefined, { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' }).format(new Date())

  if (authLoading) return <main className="auth-page"><div className="loading-state"><span className="spinner" />Checking your session…</div></main>
  if (!user) return <AuthScreen onAuthenticated={setUser} />

  return <div className="app-shell"><aside className={`sidebar ${mobileNavOpen ? 'sidebar-open' : ''}`}>
    <a className="brand" href="#home"><span className="brand-mark"><HeartPulse size={23} strokeWidth={2.2} /></span><span>care<span>point</span><small>CLINIC MANAGEMENT</small></span></a>
    <div className="nav-label">WORKSPACE</div><button className="nav-link active"><LayoutDashboard size={18} />Overview</button>
    <div className="sidebar-note"><div className="sidebar-note-icon"><Activity size={17} /></div><div><strong>Care made simple</strong><span>Manage visits with clarity.</span></div></div>
    <div className="sidebar-bottom"><button className="nav-link"><CircleHelp size={18} />Help center</button><button className="nav-link"><Settings size={18} />Settings</button><button className="profile-card signout-card" onClick={signOut}><div className="profile-avatar">{user.username.slice(0, 2).toUpperCase()}</div><div className="profile-info"><strong>{user.username}</strong><span>Sign out</span></div><ChevronDown size={16} /></button></div>
  </aside>
  {mobileNavOpen && <button className="mobile-scrim" onClick={() => setMobileNavOpen(false)} aria-label="Close navigation" />}
  <main className="main-area"><header className="topbar"><button className="mobile-menu" onClick={() => setMobileNavOpen(!mobileNavOpen)} aria-label="Toggle navigation"><Menu size={20} /></button><div className="breadcrumb">Workspace <span>/</span> <strong>Overview</strong></div><div className="topbar-right"><span className="today-label">{dateLabel}</span><button className="notification-button" aria-label="Notifications"><Bell size={18} /><i /></button><button className="top-profile signout-top" onClick={signOut}><div className="profile-avatar">{user.username.slice(0, 2).toUpperCase()}</div><span>{user.username}</span><ChevronDown size={15} /></button></div></header>
    <div className="content"><div className="page-heading"><div><div className="eyebrow">CAREPOINT PRIVATE WORKSPACE</div><h1>Good day, {user.username} <span>✦</span></h1><p>Here’s what’s happening with your appointments.</p></div><button className="button button-primary add-button" onClick={() => setFormAppointment(null)}><CalendarPlus size={17} />New appointment</button></div>
      <DashboardCards stats={stats} />
      <section className="appointments-card"><div className="section-heading"><div><h2>Appointments</h2><p>View and manage your clinic schedule</p></div><button className="refresh-button" onClick={refresh} disabled={loading}><RefreshCw size={15} className={loading ? 'spin' : ''} />Refresh</button></div>
        <SearchAndFilters filters={filters} onChange={changeFilter} onClear={() => setFilters({ search: '', status: '', doctor: '', appointment_type: '', date: '' })} />
        {loadError ? <div className="error-state"><div><h3>We couldn’t load appointments</h3><p>{loadError}</p><button className="button button-secondary" onClick={refresh}>Try again</button></div></div> : loading ? <div className="loading-state"><span className="spinner" />Loading appointments…</div> : <AppointmentTable appointments={appointments} onEdit={(item) => setFormAppointment(item)} onDelete={setDeleteAppointmentItem} />}
        <div className="table-footer"><span>Showing <strong>{appointments.length}</strong> appointment{appointments.length === 1 ? '' : 's'}</span><span>Updates are saved automatically</span></div>
      </section><footer className="page-footer">CarePoint Appointment Management <span>•</span> Demo workspace with fictional records</footer>
    </div>
  </main>
  {formAppointment !== undefined && <AppointmentForm appointment={formAppointment} onClose={() => setFormAppointment(undefined)} onSave={saveAppointment} />}
  {deleteAppointmentItem && <ConfirmDialog appointment={deleteAppointmentItem} onClose={() => setDeleteAppointmentItem(null)} onConfirm={removeAppointment} />}
  {notice && <div className="toast" role="status">{notice}</div>}
  </div>
}
