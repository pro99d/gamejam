import math

def rotate_point(point, angle_degrees):
    # Convert angle from degrees to radians
    angle_radians = math.radians(angle_degrees)
    
    # Define the rotation matrix
    cos_angle = math.cos(angle_radians)
    sin_angle = math.sin(angle_radians)

    # Perform the rotation
    x_new = point[0] * cos_angle - point[1] * sin_angle
    y_new = point[0] * sin_angle + point[1] * cos_angle

    return (x_new, y_new)

# Example usage
point = (1, 0)  # Original point
angle = 90      # Angle in degrees

rotated_point = rotate_point(point, angle)
print(f"Original point: {point}")
print(f"Rotated point by {angle} degrees: {rotated_point}")

