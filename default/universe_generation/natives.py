import random

import fo_universe_generator as fo

import planets
import statistics


def is_too_close_to_empire_home_systems(system, home_systems):
    """
    Checks if a system is too close to the player home systems.

    Player home systems should be at least 2 jumps away.
    """
    for home_system in home_systems:
        if fo.jump_distance(system, home_system) < 2:
            return True
    return False


def generate_natives(native_freq, systems, empire_home_systems):
    """
    Adds non-empire-affiliated native populations to planets.
    """

    # first, calculate the chance for natives on a planet based on the native frequency that has been passed
    # get the corresponding value for the specified natives frequency from the universe tables
    inverse_native_chance = fo.native_frequency(native_freq)
    # as the value in the universe table is higher for a lower frequency, we have to invert it
    # exception: a value of 0 means no natives, in this case return immediately
    if inverse_native_chance <= 0:
        return
    native_chance = 1.0 / float(inverse_native_chance)

    # compile a list of planets where natives can be placed
    # select only planets sufficiently far away from player home systems
    native_safe_planets = []  # list of planets safe for natives
    for candidate in systems:
        if not is_too_close_to_empire_home_systems(candidate, empire_home_systems):
            # this system is sufficiently far away from all player homeworlds, so add it's planets to our list
            native_safe_planets += fo.sys_get_planets(candidate)
    print "Number of planets far enough from players for natives to be allowed:", len(native_safe_planets)
    # if there are no "native safe" planets at all, we can stop here
    if not native_safe_planets:
        return

    # get all native species
    native_species = fo.get_native_species()
    print "Species that can be added as natives:"
    print "... " + "\n... ".join(native_species)

    # create a map with a list for each planet type containing the species
    # for which this planet type is a good environment
    # we will need this afterwards when picking natives for a planet
    natives_for_planet_type = {planet_type: [] for planet_type in planets.planet_types}
    # iterate over all native species we got
    for species in native_species:
        # check the planet environment for all planet types for this species
        for planet_type in planets.planet_types:
            # if this planet type is a good environment for the species, add it to the list for this planet type
            if fo.species_get_planet_environment(species, planet_type) == fo.planetEnvironment.good:
                natives_for_planet_type[planet_type].append(species)

    # randomly add species to planets
    # iterate over the list of "native safe" planets we compiled earlier
    for candidate in native_safe_planets:
        # make a "roll" against the chance for natives to determine if we shall place natives on this planet
        if random.random() > native_chance:
            # no, continue with next planet
            continue

        # select a native species to put on this planet
        planet_type = fo.planet_get_type(candidate)
        # check if we have any native species that like this planet type
        if not natives_for_planet_type[planet_type]:
            # no, continue with next planet
            continue
        # randomly pick one of the native species available for this planet type
        natives = random.choice(natives_for_planet_type[planet_type])

        # put the selected natives on the planet
        fo.planet_set_species(candidate, natives)
        # set planet as homeworld for that species
        fo.species_add_homeworld(natives, candidate)
        # set planet focus
        # check if the preferred focus for the native species is among the foci available on this planet
        available_foci = fo.planet_available_foci(candidate)
        preferred_focus = fo.species_preferred_focus(natives)
        if preferred_focus in available_foci:
            # if yes, set the planet focus to the preferred focus
            fo.planet_set_focus(candidate, preferred_focus)
        elif available_foci:
            # if no, and there is at least one available focus, just take the first of the list
            # otherwise don't set any focus
            fo.planet_set_focus(candidate, available_foci[0])
        print "Added native", natives, "to planet", fo.get_name(candidate)

        # increase the statistics counter for this native species, so a species summary can be dumped to the log later
        statistics.species_summary[natives] += 1