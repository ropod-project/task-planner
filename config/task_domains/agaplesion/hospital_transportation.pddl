(define (domain hospital-transportation)

    (:requirements :typing :conditional-effects)

    (:types
        location
        robot
        load
        elevator
        floor
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

        (robot_floor ?bot - robot ?floor - floor)
        (location_floor ?loc - location ?floor - floor)
        (load_floor ?load - load ?floor - floor)
        (elevator_floor ?elevator - elevator ?floor - floor)
        (destination_floor ?elevator - elevator ?floor - floor)
    )

    (:action GOTO
        :parameters (?bot - robot ?from ?to - location ?floor_from ?floor_to - floor ?load - load)
        :precondition (and
            (robot_at ?bot ?from)
            (location_floor ?from ?floor_from)
            (location_floor ?to ?floor_to)
            (= ?floor_from ?floor_to)
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
        :parameters (?bot - robot ?load - load ?loc - location ?bot_floor ?loc_floor - floor)
        :precondition (and
            (robot_at ?bot ?loc)
            (load_at ?load ?loc)
            (empty_gripper ?bot)
            (robot_floor ?bot ?bot_floor)
            (location_floor ?loc ?loc_floor)
            (= ?bot_floor ?loc_floor)
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
        :parameters (?bot - robot ?from ?to - location ?elevator - elevator ?loc_floor ?floor_from ?floor_to ?believed_floor_to - floor)
        :precondition (and
            (robot_at ?bot ?from)
            (elevator_at ?elevator ?from)
            (location_floor ?from ?floor_from)
            (location_floor ?to ?floor_to)
            (destination_floor ?elevator ?believed_floor_to)
            (not (= ?floor_from ?floor_to))
            (forall (?elevator - elevator)
                (and
                    (not (requested ?bot ?elevator))
                    (not (robot_in ?bot ?elevator))
                )
            )
        )
        :effect (and
            (not (destination_floor ?elevator ?believed_floor_to))
            (requested ?bot ?elevator)
            (destination_floor ?elevator ?floor_to)
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
        :parameters (?bot - robot ?loc - location ?elevator - elevator ?load - load)
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
            (when (and (holding ?bot ?load))
                (and (load_in ?load ?elevator))
            )
        )
    )

    (:action RIDE_ELEVATOR
        :parameters (?bot - robot ?elevator - elevator ?dest_floor - floor)
        :precondition (and
            (robot_in ?bot ?elevator)
            (destination_floor ?elevator ?dest_floor)
        )
        :effect (and
            (elevator_floor ?elevator ?dest_floor)
            (robot_floor ?bot ?dest_floor)
            (when (and (holding ?bot ?load))
                (and
                    (load_floor ?load ?dest_floor)
                )
            )
        )
    )

    (:action EXIT_ELEVATOR
        :parameters (?bot - robot ?loc - location ?elevator - elevator ?load - load ?robot_floor ?dest_floor - floor)
        :precondition (and
            (robot_in ?bot ?elevator)
            (elevator_at ?elevator ?loc)
            (arrived ?elevator)
            (robot_floor ?bot ?robot_floor)
            (destination_floor ?elevator ?dest_floor)
            (location_floor ?loc ?dest_floor)
            (= ?robot_floor ?dest_floor)
        )
        :effect (and
            (robot_at ?bot ?loc)
            (not (robot_in ?bot ?elevator))
            (not (arrived ?elevator))
            (not (requested ?bot ?elevator))
            (not (elevator_floor ?elevator ?dest_floor))
            (when (and (holding ?bot ?load))
                (and
                    (not (load_in ?load ?elevator))
                    (load_at ?load ?loc)
                )
            )
        )
    )
)
