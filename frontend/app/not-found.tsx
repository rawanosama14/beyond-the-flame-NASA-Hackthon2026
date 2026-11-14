import Link from 'next/link';
export default function NotFound(){return <div className="notfound"><span className="eyebrow">404 / UNKNOWN COORDINATES</span><h1>This path is beyond the map.</h1><p>The research destination you requested could not be found.</p><Link className="btn btn-primary" href="/dashboard">Return to mission control →</Link></div>}
