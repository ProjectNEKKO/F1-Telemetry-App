import os
import fastf1

def fetch_race_results(year=2024, round_number=1, session_type='R'):
    os.makedirs("cache", exist_ok=True)
    fastf1.Cache.enable_cache("cache")

    session = fastf1.get_session(year, round_number, session_type)
    session.load()

    results = session.results[['Position', 'Abbreviation', 'TeamName', 'Points', 'Status']].copy()
    results = results.drop_duplicates(subset=['Abbreviation']).reset_index(drop=True)
    laps = session.laps

    leader_code = results.iloc[0]['Abbreviation']
    leader_laps = laps.pick_drivers([leader_code])
    leader_laps_completed = leader_laps.shape[0]
    leader_time_total = leader_laps['LapTime'].sum()

    gap_to_leader = []
    gap_to_next = []
    status_list = []

    for idx in range(len(results)):
        driver_code = results.iloc[idx]['Abbreviation']
        original_status = str(results.iloc[idx]['Status']).strip().lower()

        # Add team color
        team_color_hex = session.get_driver(driver_code)['TeamColor']
        results.loc[idx, 'TeamColor'] = f"#{team_color_hex}"

        driver_laps = laps.pick_drivers([driver_code])
        driver_laps_completed = driver_laps.shape[0]

        # === Priority: DSQ / EXCLUDED ===
        if "dsq" in original_status or "excluded" in original_status or "disqualified" in original_status:
            status_list.append("DSQ")
            gap_to_leader.append("DSQ")
            gap_to_next.append("DSQ")
            continue

        # If no laps at all → DNF
        if driver_laps.empty:
            status_list.append("DNF")
            gap_to_leader.append("DNF")
            gap_to_next.append("DNF")
            continue

        driver_total_time = driver_laps['LapTime'].sum()

        # === Determine Status ===
        if idx == 0:
            status_list.append("Leader")
        elif driver_laps_completed < leader_laps_completed:
            if driver_laps_completed >= leader_laps_completed - 1:
                status_list.append("Lapped")
            else:
                status_list.append("DNF")
        else:
            status_list.append("Finished")

        # === GAP TO LEADER ===
        if idx == 0:
            gap_to_leader.append("Leader")
        elif status_list[-1] == "Lapped":
            laps_down = leader_laps_completed - driver_laps_completed
            gap_to_leader.append(f"+{laps_down} LAP{'S' if laps_down > 1 else ''}")
        elif status_list[-1] in ["DNF", "DSQ"]:
            gap_to_leader.append(status_list[-1])
        else:
            gap = driver_total_time - leader_time_total
            gap_to_leader.append(f"+{gap.total_seconds():.3f}s")

        # === GAP TO NEXT ===
        if idx == 0:
            gap_to_next.append("—")
        elif status_list[-1] in ["DNF", "DSQ"]:
            gap_to_next.append(status_list[-1])
        else:
            prev_code = results.iloc[idx - 1]['Abbreviation']
            prev_laps = laps.pick_drivers([prev_code])
            prev_laps_completed = prev_laps.shape[0]

            if driver_laps_completed < prev_laps_completed:
                laps_down = prev_laps_completed - driver_laps_completed
                gap_to_next.append(f"+{laps_down} LAP{'S' if laps_down > 1 else ''}")
            else:
                prev_total_time = prev_laps['LapTime'].sum()
                gap_next = abs(driver_total_time - prev_total_time)
                gap_to_next.append(f"+{gap_next.total_seconds():.3f}s")

    results['Status'] = status_list
    results['Gap to Leader'] = gap_to_leader
    results['Gap to Next'] = gap_to_next

    return results
