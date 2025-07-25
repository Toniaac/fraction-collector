from cnc_machine import CNC_Machine

cnc = CNC_Machine()

# cnc.move_to_point(0,0,0)
# cnc.move_to_point(x=270)
# cnc.move_to_point(y=150)
# cnc.move_to_point(z=-35)

locations = cnc.LOCATIONS

print(locations)

for i in range(0, 48):
    # location = cnc.get_location_position("well_plate_location", i)
    # print(f"Location {i}: {location}") 
    cnc.move_to_location('well_plate_location', i, safe=False)
    cnc.move_to_point(z=-35)
