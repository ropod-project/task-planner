(define (domain hospital-transportation)

    (:requirements :typing :conditional-effects :fluents)

    (:types
        location
        robot
        cart
        elevator
    )

    (:functions
        (robot_floor ?bot - robot) - number
        (location_floor ?loc - location) - number
        (cart_floor ?cart - cart) - number
        (elevator_floor ?elevator - elevator) - number
        (destination_floor ?elevator - elevator) - number
    )

    (:predicates
        (robot_at ?bot - robot ?loc - location)
        (robot_in ?bot - robot ?elevator - elevator)
        (cart_at ?cart - cart ?loc - location)
        (cart_in ?cart - cart ?elevator - elevator)
        (elevator_at ?elevator - elevator ?loc - location)
        (empty_gripper ?bot - robot)
        (holding ?bot - robot ?cart - cart)
        (requested ?bot - robot ?elevator - elevator)
        (arrived ?elevator - elevator)
    )

    (:action GOTO
        :parameters (?bot - robot ?from ?to - location ?cart - cart)
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
            (when (and (holding ?bot ?cart))
                (and
                    (not (cart_at ?cart ?from))
                    (cart_at ?cart ?to)
                )
            )
        )
    )

    (:action DOCK
        :parameters (?bot - robot ?cart - cart ?loc - location)
        :precondition (and
            (robot_at ?bot ?loc)
            (cart_at ?cart ?loc)
            (empty_gripper ?bot)
            (= (robot_floor ?bot) (location_floor ?loc))
        )
        :effect (and
            (not (empty_gripper ?bot))
            (holding ?bot ?cart)
        )
    )

    (:action UNDOCK
        :parameters (?bot - robot ?cart - cart)
        :precondition (and
            (holding ?bot ?cart)
        )
        :effect (and
            (not (holding ?bot ?cart))
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
        :parameters (?bot - robot ?loc - location ?dest_loc - location ?elevator - elevator ?cart - cart)
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
            (when (and (holding ?bot ?cart))
                (and (cart_in ?cart ?elevator))
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
        :parameters (?bot - robot ?loc - location ?elevator - elevator ?cart - cart)
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
            (when (and (holding ?bot ?cart))
                (and
                    (not (cart_in ?cart ?elevator))
                    (cart_at ?cart ?loc)
                    (assign (cart_floor ?cart) (elevator_floor ?elevator))
                )
            )
        )
    )
)
