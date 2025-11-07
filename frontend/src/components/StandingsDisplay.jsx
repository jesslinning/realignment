import React, { useState, useEffect, useMemo } from 'react'
import DivisionStandings from './DivisionStandings'
import ConferenceStandings from './ConferenceStandings'
import './StandingsDisplay.css'

// Define custom division order for each conference
const divisionOrder = {
  'Animals': ['Birds of Prey', 'Cats', 'Surf & Turf', 'North America'],
  'People': ['People', 'People with Jobs', 'Violent People', 'Fictional People']
}

// Get divisions in the correct order for a conference
const getOrderedDivisions = (conference, standings) => {
  if (!conference || !standings[conference]) return []
  
  const divisions = Object.keys(standings[conference])
  const customOrder = divisionOrder[conference] || []
  
  if (customOrder.length === 0) {
    // No custom order, return sorted alphabetically
    return divisions.sort()
  }
  
  // Sort divisions according to custom order
  return divisions.sort((a, b) => {
    const indexA = customOrder.indexOf(a)
    const indexB = customOrder.indexOf(b)
    
    // If both are in custom order, sort by their position
    if (indexA !== -1 && indexB !== -1) {
      return indexA - indexB
    }
    // If only one is in custom order, it comes first
    if (indexA !== -1) return -1
    if (indexB !== -1) return 1
    // If neither is in custom order, sort alphabetically
    return a.localeCompare(b)
  })
}

function StandingsDisplay({ standings, season, API_URL }) {
  const conferences = Object.keys(standings).sort()
  const [activeConference, setActiveConference] = useState(conferences[0] || '')

  // Reset active conference when standings data changes
  useEffect(() => {
    if (conferences.length > 0 && !conferences.includes(activeConference)) {
      setActiveConference(conferences[0])
    }
  }, [conferences, activeConference])

  // Get ordered divisions for the active conference
  const orderedDivisions = useMemo(() => {
    return getOrderedDivisions(activeConference, standings)
  }, [activeConference, standings])

  // Combine all teams from all divisions in the active conference
  const allConferenceTeams = useMemo(() => {
    if (!activeConference || !standings[activeConference]) return []
    
    const allTeams = []
    
    orderedDivisions.forEach((division) => {
      standings[activeConference][division].forEach((team) => {
        allTeams.push({
          ...team,
          division: division
        })
      })
    })
    
    return allTeams
  }, [activeConference, standings, orderedDivisions])

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
            {orderedDivisions.map((division) => (
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
          season={season}
          API_URL={API_URL}
        />
      </div>
    </div>
  )
}

export default StandingsDisplay

