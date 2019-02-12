(define (domain hospital-transportation)

    (:requirements :typing :conditional-effects :fluents)

    (:types
        location
        robot
        load
        elevator
    )

    (:functions
        (robot_floor ?bot - robot) - number
        (location_floor ?loc - location) - number
        (load_floor ?load - load) - number
        (elevator_floor ?elevator - elevator) - number
        (destination_floor ?elevator - elevator) - number
    )

    (:predicates
        (robot_at ?bot - robot ?loc - location)
        (robot_in ?bot - robot ?elevator - elevator)
        (load_at ?load - load ?loc - location)
        (load_in ?load - load ?elevator - elevator)
        (elevator_at ?elevator - elevator ?loc - location)
        (empty_gripper ?bot - robot)
        (holding ?bot - robot ?load - load)
        (requested ?bot - robot ?elevator - elevator)
        (arrived ?elevator - elevator)
    )

    (:action GOTO
        :parameters (?bot - robot ?from ?to - location ?load - load)
        :precondition (and
            (robot_at ?bot ?from)
            (= (location_floor ?from) (location_floor ?to))
            (forall (?elevator - elevator)
                (and
                    (not (requested ?bot ?elevator))
                    (not (robot_in ?bot ?elevator))
                )
            )
        )
        :effect (and
            (not (robot_at ?bot ?from))
            (robot_at ?bot ?to)
            (when (and (holding ?bot ?load))
                (and
                    (not (load_at ?load ?from))
                    (load_at ?load ?to)
                )
            )
        )
    )

    (:action DOCK
        :parameters (?bot - robot ?load - load ?loc - location)
        :precondition (and
            (robot_at ?bot ?loc)
            (load_at ?load ?loc)
            (empty_gripper ?bot)
            (= (robot_floor ?bot) (location_floor ?loc))
        )
        :effect (and
            (not (empty_gripper ?bot))
            (holding ?bot ?load)
        )
    )

    (:action UNDOCK
        :parameters (?bot - robot ?load - load)
        :precondition (and
            (holding ?bot ?load)
        )
        :effect (and
            (not (holding ?bot ?load))
            (empty_gripper ?bot)
        )
    )

    (:action REQUEST_ELEVATOR
        :parameters (?bot - robot ?loc - location ?elevator - elevator)
        :precondition (and
            (robot_at ?bot ?loc)
            (elevator_at ?elevator ?loc)
        )
        :effect (and
            (requested ?bot ?elevator)
            (assign (destination_floor ?elevator) (location_floor ?loc))
        )
    )

    (:action WAIT_FOR_ELEVATOR
        :parameters (?bot - robot ?elevator - elevator ?loc - location)
        :precondition (and
            (elevator_at ?elevator ?loc)
            (requested ?bot ?elevator)
        )
        :effect (and
            (arrived ?elevator)
        )
    )

    (:action ENTER_ELEVATOR
        :parameters (?bot - robot ?loc - location ?dest_loc - location ?elevator - elevator ?load - load)
        :precondition (and
            (robot_at ?bot ?loc)
            (elevator_at ?elevator ?loc)
            (requested ?bot ?elevator)
            (arrived ?elevator)
        )
        :effect (and
            (robot_in ?bot ?elevator)
            (not (robot_at ?bot ?loc))
            (not (arrived ?elevator))
            (assign (destination_floor ?elevator) (location_floor ?dest_loc))
            (when (and (holding ?bot ?load))
                (and (load_in ?load ?elevator))
            )
        )
    )

    (:action RIDE_ELEVATOR
        :parameters (?bot - robot ?elevator - elevator)
        :precondition (and
            (robot_in ?bot ?elevator)
        )
        :effect (and
            (assign (elevator_floor ?elevator) (destination_floor ?elevator))
            (assign (robot_floor ?bot) (destination_floor ?elevator))
        )
    )

    (:action EXIT_ELEVATOR
        :parameters (?bot - robot ?loc - location ?elevator - elevator ?load - load)
        :precondition (and
            (robot_in ?bot ?elevator)
            (elevator_at ?elevator ?loc)
            (arrived ?elevator)
            (= (elevator_floor ?elevator) (destination_floor ?elevator))
            (= (location_floor ?loc) (elevator_floor ?elevator))
        )
        :effect (and
            (robot_at ?bot ?loc)
            (not (robot_in ?bot ?elevator))
            (not (arrived ?elevator))
            (not (requested ?bot ?elevator))
            (assign (robot_floor ?bot) (elevator_floor ?elevator))
            (when (and (holding ?bot ?load))
                (and
                    (not (load_in ?load ?elevator))
                    (load_at ?load ?loc)
                    (assign (load_floor ?load) (elevator_floor ?elevator))
                )
            )
        )
    )
)
