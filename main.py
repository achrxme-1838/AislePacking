import GlobalPlanner
import time

packed_obj_list = []


def algorithm_evaluation():
    aisle_area = GlobalPlanner.AISLE_DEPTH * (GlobalPlanner.AISLE_WIDTH - GlobalPlanner.CURRENT_MAX_WIDTH)
    packed_area = 0
    for obj in packed_obj_list:
        packed_area += obj.width * obj.height

    return packed_area / aisle_area * 100


def main():
    global_planner = GlobalPlanner.GlobalPlanner()

    idx = 1
    while 1:
        obj = GlobalPlanner.object_generator('INT', idx, GlobalPlanner.CURRENT_MAX_WIDTH,
                                             GlobalPlanner.CURRENT_MAX_HEIGHT)

        start_time = time.time()
        result = global_planner.packing_algorithm(obj, 'NEAREST')
        # result = global_planner.packing_algorithm(obj, 'MIN_HEIGHT')
        # result = global_planner.packing_algorithm(obj, 'MIN_HEIGHT_WIDTH')
        # result = global_planner.packing_algorithm(obj, 'RANDOM')

        end_time = time.time()

        if result == 'Fail':
            global_planner.state_representor.draw_potential_points(global_planner.potential_points)
            GlobalPlanner.StateRepresentor.plt.draw()
            print("===============================")
            print('Successfully packed ', idx - 1, ' objects')
            print('Cannot packing', obj)

            print(algorithm_evaluation())

            break
        else:
            print('Object : ', idx, ' (Operating time : ', end_time - start_time, ')')
            packed_obj_list.append(obj)
            idx += 1
            GlobalPlanner.StateRepresentor.plt.draw()
            GlobalPlanner.StateRepresentor.plt.pause(0.0000001)

    GlobalPlanner.StateRepresentor.plt.show()

    # total_result = []
    #
    # for i in range(100):
    #     global_planner = GlobalPlanner()
    #
    #     idx = 1
    #     while 1:
    #         obj = object_generator('FLOAT', idx, CURRENT_MAX_WIDTH, CURRENT_MAX_HEIGHT)
    #         # result = global_planner.packing_algorithm(obj, 'NEAREST')
    #         result = global_planner.packing_algorithm(obj, 'MIN_HEIGHT')
    #         # result = global_planner.packing_algorithm(obj, 'MIN_HEIGHT_WIDTH')
    #         # result = global_planner.packing_algorithm(obj, 'RANDOM')
    #
    #         if result == 'Fail':
    #             print("END", i)
    #             # print(algorithm_evaluation())
    #             total_result.append(algorithm_evaluation())
    #             packed_obj_list.clear()
    #             break
    #         else:
    #             packed_obj_list.append(obj)
    #             idx += 1
    #
    # print(total_result)
    # print(sum(total_result)/len(total_result))


if __name__ == "__main__":
    main()
