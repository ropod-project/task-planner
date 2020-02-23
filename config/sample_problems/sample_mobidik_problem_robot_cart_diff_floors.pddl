(define (problem mobidik-transportation)
    (:domain hospital-transportation)

    (:objects
        frank - robot
        charging_station somewhere_on_floor1 pickup_location delivery_location elevator0 elevator1 elevator2 - location
        mobidik - load
        toma_elevator - elevator
        floor0 floor1 floor2 unknown - floor
    )

    (:init
        (robot_floor frank floor1)
        (load_floor mobidik floor0)
        (location_floor charging_station floor0)
        (location_floor pickup_location floor0)
        (location_floor somewhere_on_floor1 floor1)
        (location_floor elevator0 floor0)
        (location_floor elevator1 floor1)
        (location_floor elevator2 floor2)
        (location_floor delivery_location floor2)
        (elevator_floor toma_elevator unknown)
        (destination_floor toma_elevator unknown)

        (robot_at frank somewhere_on_floor1)
        (load_at mobidik pickup_location)
        (elevator_at toma_elevator elevator0)
        (elevator_at toma_elevator elevator1)
        (elevator_at toma_elevator elevator2)
        (empty_gripper frank)
    )

    (:goal
        (and
            (load_at mobidik delivery_location)
            (empty_gripper frank)
        )
    )
)
