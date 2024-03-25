import os


def generate_waypoints(point_list, file_name):
    file_name = f'../waypoints/{file_name}'
    point_list.append(point_list[0])
    with open(file_name, 'w') as f:
        f.write('QGC WPL 110\n')
        f.write(f'0\t0\t3\t16\t0.00000000\t0.00000000\t0.00000000\t0.00000000\t{point_list[0][0]:.8f}'
                f''f'\t{point_list[0][1]:.8f}\t0.00000000\t1\n')
        for number, point in enumerate(point_list):
            f.write(formatted_line(number + 1, point, len(point_list)))


def formatted_line(number, point, total_num):
    pitch_angle = 0
    altitude = 60
    if (number == 1):
        pitch_angle = 25
        altitude = 30

    if number == total_num - 2:
        altitude = 45

    if number == total_num - 1:
        altitude = 30

    if number == total_num - 0:
        altitude = 15

    return f'{number}\t0\t3\t16\t{pitch_angle:.8f}\t0.00000000\t0.00000000\t0.00000000\t{point[0]:.8f}' \
           f'\t{point[1]:.8f}\t{altitude:.8f}\t1\n'
