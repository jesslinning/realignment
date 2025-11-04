import React, { useState, useEffect, useMemo } from 'react'
import DivisionStandings from './DivisionStandings'
import ConferenceStandings from './ConferenceStandings'
import './StandingsDisplay.css'

function StandingsDisplay({ standings }) {
  const conferences = Object.keys(standings).sort()
  const [activeConference, setActiveConference] = useState(conferences[0] || '')

  // Reset active conference when standings data changes
  useEffect(() => {
    if (conferences.length > 0 && !conferences.includes(activeConference)) {
      setActiveConference(conferences[0])
    }
  }, [conferences, activeConference])

  // Combine all teams from all divisions in the active conference
  const allConferenceTeams = useMemo(() => {
    if (!activeConference || !standings[activeConference]) return []
    
    const allTeams = []
    Object.keys(standings[activeConference]).forEach((division) => {
      standings[activeConference][division].forEach((team) => {
        allTeams.push({
          ...team,
          division: division
        })
      })
    })
    
    return allTeams
  }, [activeConference, standings])

  if (conferences.length === 0) {
    return <div className="standings-display">No standings available</div>
  }

  return (
    <div className="standings-display">
      <div className="tabs">
        {conferences.map((conference) => (
          <button
            key={conference}
            className={`tab ${activeConference === conference ? 'active' : ''}`}
            onClick={() => setActiveConference(conference)}
          >
            {conference} Conference
          </button>
        ))}
      </div>
      
      <div className="conference-content">
        <div className="conference">
          <div className="divisions">
            {Object.keys(standings[activeConference]).map((division) => (
              <DivisionStandings
                key={division}
                conference={activeConference}
                division={division}
                teams={standings[activeConference][division]}
              />
            ))}
          </div>
        </div>
        
        <ConferenceStandings
          conference={activeConference}
          teams={allConferenceTeams}
        />
      </div>
    </div>
  )
}

export default StandingsDisplay

