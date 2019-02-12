(define (problem mobidik-transportation)
    (:domain hospital-transportation)

    (:objects
        frank - robot
        charging_station somewhere_on_floor1 pickup_location delivery_location elevator0 elevator1 elevator2 - location
        mobidik - load
        toma_elevator - elevator
    )

    (:init
        (= (robot_floor frank) 1)
        (= (load_floor mobidik) 0)
        (= (location_floor charging_station) 0)
        (= (location_floor pickup_location) 0)
        (= (location_floor somewhere_on_floor1) 1)
        (= (location_floor elevator0) 0)
        (= (location_floor elevator1) 1)
        (= (location_floor elevator2) 2)
        (= (location_floor delivery_location) 2)
        (= (elevator_floor toma_elevator) 100)
        (= (destination_floor toma_elevator) 100)

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
