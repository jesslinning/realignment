import React from 'react'
import './DivisionStandings.css'

function DivisionStandings({ conference, division, teams }) {
  const formatWinPct = (pct) => {
    if (isNaN(pct) || pct === null) return '0.000'
    return pct.toFixed(3)
  }

  return (
    <div className="division-standings">
      <h3 className="division-title">{division}</h3>
      <table className="standings-table">
        <thead>
          <tr>
            <th>Rank</th>
            <th>Team</th>
            <th>W</th>
            <th>L</th>
            <th>T</th>
            <th>Pct</th>
          </tr>
        </thead>
        <tbody>
          {teams.map((team, index) => (
            <tr key={team.team} className={index === 0 ? 'leader' : ''}>
              <td className="rank">{index + 1}</td>
              <td className="team-name">
                <span className="team-abbr">{team.team}</span>
                <span className="team-full">{team.name}</span>
              </td>
              <td>{team.wins}</td>
              <td>{team.losses}</td>
              <td>{team.ties}</td>
              <td className="win-pct">{formatWinPct(team.win_pct)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default DivisionStandings

