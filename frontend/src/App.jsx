import { useEffect, useMemo, useState } from 'react';

const DEFAULT_API = import.meta.env.VITE_API_BASE_URL || 'https://ticket-booking-system-1-okvo.onrender.com';
const DEFAULT_LAYOUT = {
  stage_label: 'STAGE',
  rows: Array.from({ length: 5 }, (_, index) => ({
    label: String.fromCharCode(65 + index),
    seats: Array.from({ length: 5 }, (_, seatIndex) => `${String.fromCharCode(65 + index)}${seatIndex + 1}`),
  })),
};

function App() {
  const [apiBase, setApiBase] = useState(DEFAULT_API);
  const [token, setToken] = useState('');
  const [currentRole, setCurrentRole] = useState('guest');
  const [currentUserName, setCurrentUserName] = useState('');
  const [noticeState, setNoticeState] = useState({
    type: 'info',
    text: 'Use the register and login panels to enter the system, then browse events and book tickets.',
  });
  const [registerForm, setRegisterForm] = useState({
    email: 'customer@booking.com',
    password: 'secret123',
    full_name: 'Demo Customer',
    role_name: 'customer',
  });
  const [loginForm, setLoginForm] = useState({
    username: 'customer@booking.com',
    password: 'secret123',
  });
  const [venueForm, setVenueForm] = useState({
    name: 'Grand Arena',
    city: 'Mumbai',
    address: 'Marine Drive',
    capacity: 1200,
    description: 'Premium concert venue',
  });
  const [seatCategoryForm, setSeatCategoryForm] = useState({
    venue_id: 1,
    name: 'VIP',
    description: 'Premium seating',
    price_multiplier: 2.0,
  });
  const [eventForm, setEventForm] = useState({
    title: 'Sunset Live',
    description: 'Live concert event',
    venue_id: 1,
    start_time: '2026-08-01T18:00:00',
    end_time: '2026-08-01T22:00:00',
    status: 'published',
  });
  const [venues, setVenues] = useState([]);
  const [events, setEvents] = useState([]);
  const [selectedEventId, setSelectedEventId] = useState('');
  const [seatMap, setSeatMap] = useState({
    event_id: null,
    venue_id: null,
    available: 0,
    hold_ttl_seconds: 60,
    seat_categories: [],
    layout: DEFAULT_LAYOUT,
  });
  const [selectedCategoryId, setSelectedCategoryId] = useState('');
  const [bookingQuantity, setBookingQuantity] = useState(1);
  const [selectedSeats, setSelectedSeats] = useState([]);
  const [ticketSummary, setTicketSummary] = useState('');
  const [ticketDetails, setTicketDetails] = useState(null);

  const apiUrl = useMemo(() => apiBase.replace(/\/$/, ''), [apiBase]);
  const selectedCategory = useMemo(
    () =>
      seatMap.seat_categories.find(
        (category) => Number(category.seat_category_id) === Number(selectedCategoryId),
      ),
    [seatMap, selectedCategoryId],
  );
  const selectedEvent = useMemo(
    () => events.find((event) => Number(event.id) === Number(selectedEventId)) ?? null,
    [events, selectedEventId],
  );
  const layoutRows = seatMap.layout?.rows ?? DEFAULT_LAYOUT.rows;

  useEffect(() => {
    setSelectedSeats([]);
    setBookingQuantity(1);
  }, [selectedEventId, selectedCategoryId]);

  useEffect(() => {
    fetchEvents();
    fetchVenues();
  }, []);

  function setBanner(type, text) {
    setNoticeState({ type, text });
  }

  function extractErrorMessage(payload) {
    if (Array.isArray(payload?.detail)) {
      return payload.detail.map((item) => item.msg).join(' • ');
    }
    if (typeof payload?.detail === 'string') {
      return payload.detail;
    }
    return JSON.stringify(payload ?? {});
  }

  async function requestJson(url, options = {}) {
    const response = await fetch(url, options);
    const text = await response.text();
    const payload = text ? JSON.parse(text) : null;
    return { response, payload };
  }

  async function fetchCurrentUserProfile(authToken) {
    const { response, payload } = await requestJson(`${apiUrl}/api/v1/auth/me`, {
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
    });

    if (response.ok) {
      setCurrentRole(payload.role_name);
      setCurrentUserName(payload.full_name);
      setBanner('success', `Signed in as ${payload.full_name} (${payload.role_name}).`);
    } else {
      setBanner('error', `Profile error: ${extractErrorMessage(payload)}`);
    }
  }

  async function registerUser() {
    const { response, payload } = await requestJson(`${apiUrl}/api/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(registerForm),
    });

    if (response.ok) {
      setBanner('success', `Registered ${payload.email} as ${payload.role_name}.`);
      return;
    }

    setBanner('error', `Registration failed: ${extractErrorMessage(payload)}`);
  }

  async function loginUser() {
    const formData = new URLSearchParams();
    formData.append('username', loginForm.username);
    formData.append('password', loginForm.password);

    const { response, payload } = await requestJson(`${apiUrl}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData,
    });

    if (!response.ok) {
      setBanner('error', `Login failed: ${extractErrorMessage(payload)}`);
      return;
    }

    const nextToken = payload.access_token ?? '';
    setToken(nextToken);

    if (nextToken) {
      await fetchCurrentUserProfile(nextToken);
    }
  }

  async function createVenue() {
    if (!token) {
      setBanner('error', 'Login first as an admin to create venues.');
      return;
    }

    const { response, payload } = await requestJson(`${apiUrl}/api/v1/venues`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(venueForm),
    });

    if (response.ok) {
      setBanner('success', `Venue created: ${payload.name}.`);
      await fetchVenues();
      return;
    }

    setBanner('error', `Venue creation failed: ${extractErrorMessage(payload)}`);
  }

  async function createSeatCategory() {
    if (!token) {
      setBanner('error', 'Login first as an admin to create seat categories.');
      return;
    }

    const { response, payload } = await requestJson(
      `${apiUrl}/api/v1/venues/${seatCategoryForm.venue_id}/seat-categories`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: seatCategoryForm.name,
          description: seatCategoryForm.description,
          price_multiplier: Number(seatCategoryForm.price_multiplier),
        }),
      },
    );

    if (response.ok) {
      setBanner('success', `Seat category created: ${payload.name}.`);
      await fetchVenues();
      return;
    }

    setBanner('error', `Seat category creation failed: ${extractErrorMessage(payload)}`);
  }

  async function createEvent() {
    if (!token) {
      setBanner('error', 'Login first as an organizer or admin to create an event.');
      return;
    }

    const { response, payload } = await requestJson(`${apiUrl}/api/v1/events`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        title: eventForm.title,
        description: eventForm.description,
        venue_id: Number(eventForm.venue_id),
        start_time: eventForm.start_time,
        end_time: eventForm.end_time,
        status: eventForm.status,
      }),
    });

    if (response.ok) {
      setBanner('success', `Event created: ${payload.title}.`);
      await fetchEvents();
      return;
    }

    setBanner('error', `Event creation failed: ${extractErrorMessage(payload)}`);
  }

  async function fetchVenues() {
    const { response, payload } = await requestJson(`${apiUrl}/api/v1/venues`);

    if (response.ok) {
      setVenues(payload);
      setBanner('info', `Loaded ${payload.length} venues.`);
      return;
    }

    setBanner('error', `Venue list failed: ${extractErrorMessage(payload)}`);
  }

  async function fetchEvents() {
    const { response, payload } = await requestJson(`${apiUrl}/api/v1/events`);

    if (response.ok) {
      setEvents(payload);
      setBanner('info', `Loaded ${payload.length} events.`);
      return;
    }

    setBanner('error', `Event list failed: ${extractErrorMessage(payload)}`);
  }

  async function fetchSeatMap(eventId) {
    const { response, payload } = await requestJson(`${apiUrl}/api/v1/events/${eventId}/seat-map`);

    if (!response.ok) {
      setBanner('error', `Seat map error: ${extractErrorMessage(payload)}`);
      return;
    }

    setSeatMap(payload);
    setSelectedEventId(eventId);
    setSelectedSeats([]);
    setBookingQuantity(1);
    if (payload.seat_categories?.length > 0) {
      setSelectedCategoryId(Number(payload.seat_categories[0].seat_category_id));
    }
    setBanner('info', `Seat map loaded for event ${eventId}.`);
  }

  async function createBooking() {
    if (!selectedEventId || !selectedCategoryId || !token) {
      setBanner('error', 'Sign in as a customer, choose an event, and pick a category before booking.');
      return;
    }

    const requestedQuantity = selectedSeats.length > 0 ? selectedSeats.length : Number(bookingQuantity);

    if (selectedCategory && requestedQuantity > Number(selectedCategory.available)) {
      setBanner('error', `Only ${selectedCategory.available} seats remain in ${selectedCategory.name}.`);
      return;
    }

    const { response, payload } = await requestJson(`${apiUrl}/api/v1/bookings`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        event_id: Number(selectedEventId),
        seat_category_id: Number(selectedCategoryId),
        quantity: requestedQuantity,
      }),
    });

    if (response.ok) {
      const selectedSeatSummary = selectedSeats.length > 0 ? ` • Seats ${selectedSeats.join(', ')}` : '';
      setTicketSummary(
        `${selectedEvent?.title ?? 'Your event'} • ${payload.quantity} ticket(s)${selectedSeatSummary} • Reference ${payload.ticket_reference ?? 'N/A'} • QR ${payload.qr_payload ?? 'N/A'}`,
      );
      setTicketDetails({
        reference: payload.ticket_reference ?? 'N/A',
        code: payload.ticket_code ?? payload.ticket_reference ?? 'N/A',
        qrCode: payload.qr_code ?? payload.qr_payload ?? '',
      });
      setBanner('success', `Confirmed booking #${payload.id}.`);
      setSelectedSeats([]);
      setBookingQuantity(1);
      await fetchSeatMap(selectedEventId);
      return;
    }

    setBanner('error', `Booking failed: ${extractErrorMessage(payload)}`);
  }

  async function healthCheck() {
    const { response, payload } = await requestJson(`${apiUrl}/health`);

    if (response.ok) {
      setBanner('success', `System health: ${payload.status} (${payload.database}).`);
      return;
    }

    setBanner('error', `Health check failed: ${extractErrorMessage(payload)}`);
  }

  function logoutUser() {
    setToken('');
    setCurrentRole('guest');
    setCurrentUserName('');
    setSelectedSeats([]);
    setTicketSummary('');
    setTicketDetails(null);
    setBanner('info', 'Logged out. You can log in again at any time.');
  }

  function handleSeatPick(seatLabel, rowIndex) {
    const categoryMeta = getSeatCategoryMeta(seatLabel, rowIndex);
    const matchingCategory = seatMap.seat_categories.find(
      (category) => category.name === categoryMeta.name,
    );
    const activeCategory = selectedCategory ?? matchingCategory ?? seatMap.seat_categories[0];
    const maxAllowed = activeCategory ? Number(activeCategory.available) : Number.POSITIVE_INFINITY;

    if (selectedSeats.includes(seatLabel)) {
      setSelectedSeats((current) => current.filter((seat) => seat !== seatLabel));
      setBookingQuantity(Math.max(1, selectedSeats.length - 1));
      return;
    }

    if (selectedSeats.length >= maxAllowed) {
      setBanner('error', `Only ${maxAllowed} seats remain in ${activeCategory?.name ?? 'this category'}.`);
      return;
    }

    setSelectedSeats((current) => [...current, seatLabel]);
    setBookingQuantity(selectedSeats.length + 1);
  }

  function getSeatCategoryMeta(seatLabel, rowIndex) {
    if (!seatMap.seat_categories?.length) {
      return { name: 'Standard', className: 'seat-pill--standard' };
    }

    const categoryIndex = rowIndex % Math.max(1, seatMap.seat_categories.length);
    const category = seatMap.seat_categories[categoryIndex] ?? seatMap.seat_categories[0];
    const normalizedName = (category.name || '').toLowerCase();
    const className = normalizedName.includes('vip') ? 'seat-pill--vip' : 'seat-pill--standard';

    return { name: category.name, className };
  }

  const roleLabel =
    currentRole === 'guest' ? 'Guest' : currentRole.charAt(0).toUpperCase() + currentRole.slice(1);

  return (
    <div className="app-shell">
      <header className="hero-card">
        <div>
          <p className="eyebrow">Live ticket booking</p>
          <h1>BookMyShow-style ticketing portal</h1>
          <p className="hero-copy">
            Browse venues and events, inspect seat availability by category, hold seats, and
            confirm live bookings in a clean customer-first flow.
          </p>
        </div>
        <div className="status-box">
          <label className="field-label">
            API Base
            <input value={apiBase} onChange={(e) => setApiBase(e.target.value)} />
          </label>
          <div className="role-banner">
            <strong>Session</strong>
            <span>
              {currentUserName
                ? `${currentUserName} • ${roleLabel}`
                : `Logged in as ${roleLabel}`}
            </span>
            {token ? <button onClick={logoutUser}>Logout</button> : null}
          </div>
        </div>
      </header>

      <main className="grid-layout">
        <section className="panel">
          <h2>Register</h2>
          <div className="stack">
            <input
              value={registerForm.email}
              onChange={(e) => setRegisterForm({ ...registerForm, email: e.target.value })}
              placeholder="Email"
            />
            <input
              value={registerForm.full_name}
              onChange={(e) => setRegisterForm({ ...registerForm, full_name: e.target.value })}
              placeholder="Full name"
            />
            <input
              value={registerForm.password}
              onChange={(e) => setRegisterForm({ ...registerForm, password: e.target.value })}
              placeholder="Password"
            />
            <select
              value={registerForm.role_name}
              onChange={(e) => setRegisterForm({ ...registerForm, role_name: e.target.value })}
            >
              <option value="admin">admin</option>
              <option value="organizer">organizer</option>
              <option value="customer">customer</option>
            </select>
            <button onClick={registerUser}>Register</button>
          </div>
        </section>

        <section className="panel">
          <h2>Login</h2>
          <div className="stack">
            <input
              value={loginForm.username}
              onChange={(e) => setLoginForm({ ...loginForm, username: e.target.value })}
              placeholder="Email"
            />
            <input
              value={loginForm.password}
              onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
              placeholder="Password"
            />
            <button onClick={loginUser}>Login</button>
            <div className="token-box">{token || 'No token yet'}</div>
          </div>
        </section>

        {currentRole === 'admin' ? (
          <section className="panel wide">
            <h2>Admin actions</h2>
            <div className="stack">
              <div className="form-grid">
                <input
                  value={venueForm.name}
                  onChange={(e) => setVenueForm({ ...venueForm, name: e.target.value })}
                  placeholder="Venue name"
                />
                <input
                  value={venueForm.city}
                  onChange={(e) => setVenueForm({ ...venueForm, city: e.target.value })}
                  placeholder="City"
                />
                <input
                  value={venueForm.address}
                  onChange={(e) => setVenueForm({ ...venueForm, address: e.target.value })}
                  placeholder="Address"
                />
                <input
                  value={venueForm.capacity}
                  type="number"
                  onChange={(e) => setVenueForm({ ...venueForm, capacity: Number(e.target.value) })}
                  placeholder="Capacity"
                />
                <input
                  value={venueForm.description}
                  onChange={(e) => setVenueForm({ ...venueForm, description: e.target.value })}
                  placeholder="Description"
                />
              </div>
              <button onClick={createVenue}>Create venue</button>
            </div>

            <div className="stack spacer-top">
              <div className="form-grid">
                <input
                  value={seatCategoryForm.venue_id}
                  type="number"
                  onChange={(e) =>
                    setSeatCategoryForm({ ...seatCategoryForm, venue_id: Number(e.target.value) })
                  }
                  placeholder="Venue ID"
                />
                <input
                  value={seatCategoryForm.name}
                  onChange={(e) => setSeatCategoryForm({ ...seatCategoryForm, name: e.target.value })}
                  placeholder="Seat category"
                />
                <input
                  value={seatCategoryForm.description}
                  onChange={(e) =>
                    setSeatCategoryForm({ ...seatCategoryForm, description: e.target.value })
                  }
                  placeholder="Category description"
                />
                <input
                  value={seatCategoryForm.price_multiplier}
                  type="number"
                  step="0.1"
                  onChange={(e) =>
                    setSeatCategoryForm({
                      ...seatCategoryForm,
                      price_multiplier: Number(e.target.value),
                    })
                  }
                  placeholder="Price multiplier"
                />
              </div>
              <button onClick={createSeatCategory}>Create seat category</button>
            </div>

            <div className="stack spacer-top">
              <div className="form-grid">
                <input
                  value={eventForm.title}
                  onChange={(e) => setEventForm({ ...eventForm, title: e.target.value })}
                  placeholder="Event title"
                />
                <input
                  value={eventForm.venue_id}
                  type="number"
                  onChange={(e) => setEventForm({ ...eventForm, venue_id: Number(e.target.value) })}
                  placeholder="Venue ID"
                />
                <input
                  value={eventForm.start_time}
                  onChange={(e) => setEventForm({ ...eventForm, start_time: e.target.value })}
                  placeholder="Start time"
                />
                <input
                  value={eventForm.end_time}
                  onChange={(e) => setEventForm({ ...eventForm, end_time: e.target.value })}
                  placeholder="End time"
                />
                <input
                  value={eventForm.description}
                  onChange={(e) => setEventForm({ ...eventForm, description: e.target.value })}
                  placeholder="Description"
                />
                <select
                  value={eventForm.status}
                  onChange={(e) => setEventForm({ ...eventForm, status: e.target.value })}
                >
                  <option value="draft">draft</option>
                  <option value="published">published</option>
                  <option value="cancelled">cancelled</option>
                </select>
              </div>
              <button onClick={createEvent}>Create event</button>
            </div>
          </section>
        ) : null}

        {currentRole === 'organizer' ? (
          <section className="panel wide">
            <h2>Organizer actions</h2>
            <div className="stack">
              <div className="form-grid">
                <input
                  value={eventForm.title}
                  onChange={(e) => setEventForm({ ...eventForm, title: e.target.value })}
                  placeholder="Event title"
                />
                <input
                  value={eventForm.venue_id}
                  type="number"
                  onChange={(e) => setEventForm({ ...eventForm, venue_id: Number(e.target.value) })}
                  placeholder="Venue ID"
                />
                <input
                  value={eventForm.start_time}
                  onChange={(e) => setEventForm({ ...eventForm, start_time: e.target.value })}
                  placeholder="Start time"
                />
                <input
                  value={eventForm.end_time}
                  onChange={(e) => setEventForm({ ...eventForm, end_time: e.target.value })}
                  placeholder="End time"
                />
                <input
                  value={eventForm.description}
                  onChange={(e) => setEventForm({ ...eventForm, description: e.target.value })}
                  placeholder="Description"
                />
                <select
                  value={eventForm.status}
                  onChange={(e) => setEventForm({ ...eventForm, status: e.target.value })}
                >
                  <option value="draft">draft</option>
                  <option value="published">published</option>
                  <option value="cancelled">cancelled</option>
                </select>
              </div>
              <button onClick={createEvent}>Create event</button>
            </div>
          </section>
        ) : null}

        {currentRole === 'customer' ? (
          <section className="panel wide">
            <h2>Customer booking flow</h2>
            <div className="button-row">
              <button onClick={fetchVenues}>Browse venues</button>
              <button onClick={fetchEvents}>Browse events</button>
              <button onClick={healthCheck}>Check system health</button>
            </div>

            <div className="event-list">
              {events.map((event) => (
                <article className="event-card" key={event.id}>
                  <div>
                    <strong>{event.title}</strong>
                    <p>{event.description || 'No description'}</p>
                    <span className="muted-copy">{new Date(event.start_time).toLocaleString()}</span>
                  </div>
                  <button onClick={() => fetchSeatMap(event.id)}>View seats</button>
                </article>
              ))}
            </div>

            {selectedEvent ? (
              <div className="event-highlight">
                <strong>{selectedEvent.title}</strong>
                <span>{selectedEvent.description || 'Live event'}</span>
                <span className="muted-copy">{new Date(selectedEvent.start_time).toLocaleString()}</span>
              </div>
            ) : null}

            {seatMap.seat_categories.length > 0 ? (
              <div className="seat-map-card">
                <div className="seat-header">
                  <div>
                    <strong>Choose your seats</strong>
                    <p className="muted-copy">Secure your booking for {seatMap.hold_ttl_seconds}s before checkout expires.</p>
                  </div>
                  <div className="stat-badge">{seatMap.available} tickets still open</div>
                </div>

                <div className="venue-stage">{seatMap.layout?.stage_label ?? 'STAGE'}</div>
                <div className="seat-legend">
                  {seatMap.seat_categories.map((category) => {
                    const isVip = (category.name || '').toLowerCase().includes('vip');
                    return (
                      <span
                        key={category.seat_category_id}
                        className={`seat-legend__item ${isVip ? 'seat-legend__item--vip' : 'seat-legend__item--standard'}`}
                      >
                        {category.name}
                      </span>
                    );
                  })}
                </div>
                <div className="seat-map-grid">
                  {layoutRows.map((row, rowIndex) => (
                    <div className="row-block" key={row.label}>
                      <div className="row-label">{row.label}</div>
                      {row.seats.map((seatLabel) => {
                        const meta = getSeatCategoryMeta(seatLabel, rowIndex);
                        const isSelected = selectedSeats.includes(seatLabel);
                        return (
                          <button
                            key={seatLabel}
                            type="button"
                            className={`seat-pill ${meta.className} ${isSelected ? 'seat-pill--selected' : ''}`}
                            onClick={() => handleSeatPick(seatLabel, rowIndex)}
                          >
                            <span className="seat-pill__label">{seatLabel}</span>
                            <span className="seat-pill__tag">{meta.name}</span>
                          </button>
                        );
                      })}
                    </div>
                  ))}
                </div>

                <div className="seat-category-list">
                  {seatMap.seat_categories.map((category) => (
                    <button
                      key={category.seat_category_id}
                      className={`seat-category-chip ${
                        Number(selectedCategoryId) === Number(category.seat_category_id)
                          ? 'seat-category-chip--active'
                          : ''
                      }`}
                      onClick={() => setSelectedCategoryId(Number(category.seat_category_id))}
                    >
                      {category.name} • {category.available} left • {category.price_multiplier}x
                    </button>
                  ))}
                </div>

                <div className="booking-controls">
                  <label>
                    Quantity
                    <input
                      type="number"
                      min="1"
                      value={selectedSeats.length > 0 ? selectedSeats.length : bookingQuantity}
                      onChange={(e) => {
                        setBookingQuantity(Number(e.target.value) || 1);
                        if (selectedSeats.length > 0) {
                          setSelectedSeats([]);
                        }
                      }}
                    />
                  </label>
                  <button onClick={createBooking}>
                    {selectedSeats.length > 0 ? `Reserve ${selectedSeats.length} selected` : 'Reserve now'}
                  </button>
                </div>

                {selectedSeats.length > 0 ? (
                  <div className="summary-card">
                    <strong>Selected seats</strong>
                    <span>{selectedSeats.join(', ')}</span>
                  </div>
                ) : null}

                {selectedCategory ? (
                  <div className="summary-card">
                    <strong>{selectedCategory.name}</strong>
                    <span>{selectedCategory.description || 'Premium seating'}</span>
                    <span>{selectedCategory.available} seats remaining</span>
                  </div>
                ) : null}

                {ticketSummary ? <div className="ticket-card">{ticketSummary}</div> : null}

                {ticketDetails ? (
                  <div className="ticket-card ticket-card--detail">
                    <div className="ticket-card__header">
                      <strong>Your ticket</strong>
                      <span>Ready to show at entry</span>
                    </div>
                    <div className="ticket-card__body">
                      <div>
                        <div className="ticket-card__label">Reference</div>
                        <div className="ticket-card__value">{ticketDetails.reference}</div>
                      </div>
                      <div>
                        <div className="ticket-card__label">Code</div>
                        <div className="ticket-card__value">{ticketDetails.code}</div>
                      </div>
                    </div>
                    {ticketDetails.qrCode ? (
                      <img className="ticket-qr" src={ticketDetails.qrCode} alt="Booking QR code" />
                    ) : null}
                  </div>
                ) : null}
              </div>
            ) : null}
          </section>
        ) : null}

        <section className="panel wide">
          <h2>Live status</h2>
          <div className={`notice-banner notice-banner--${noticeState.type}`}>{noticeState.text}</div>
        </section>
      </main>
    </div>
  );
}

export default App;
