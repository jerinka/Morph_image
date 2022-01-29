#!/bin/env python3

import cv2
import numpy as np

def get_triangulation_indices(points):
    """Get indices triples for every triangle
    """
    # Bounding rectangle
    bounding_rect = (*points.min(axis=0), *points.max(axis=0))

    # Triangulate all points
    subdiv = cv2.Subdiv2D(bounding_rect)
    #import pdb;pdb.set_trace()

    pt_list = [(int(p[0]),int(p[1])) for p in points]
    subdiv.insert(pt_list)

    # Iterate over all triangles
    for x1, y1, x2, y2, x3, y3 in subdiv.getTriangleList():
        # Get index of all points
        yield [(points==point).all(axis=1).nonzero()[0][0] for point in [(x1,y1), (x2,y2), (x3,y3)]]

def crop_to_triangle(img, triangle):
    """Crop image to triangle
    """
    # Get bounding rectangle
    bounding_rect = cv2.boundingRect(triangle)

    # Crop image to bounding box
    img_cropped = img[bounding_rect[1]:bounding_rect[1] + bounding_rect[3],
                      bounding_rect[0]:bounding_rect[0] + bounding_rect[2]]
    # Move triangle to coordinates in cropped image
    triangle_cropped = [(point[0]-bounding_rect[0], point[1]-bounding_rect[1]) for point in triangle]
    return triangle_cropped, img_cropped

def transform(src_img, src_points, dst_img, dst_points): 
    """Transforms source image to target image, overwriting the target image.
    """
    src_points = np.array(src_points, np.int32)
    dst_points = np.array(dst_points, np.int32)

    for indices in get_triangulation_indices(src_points):
        # Get triangles from indices
        #import pdb;pdb.set_trace()
        

        src_triangle = src_points[indices]
        dst_triangle = dst_points[indices]

        # Crop to triangle, to make calculations more efficient
        src_triangle_cropped, src_img_cropped = crop_to_triangle(src_img, src_triangle)
        dst_triangle_cropped, dst_img_cropped = crop_to_triangle(dst_img, dst_triangle)

        # Calculate transfrom to warp from old image to new
        transform = cv2.getAffineTransform(np.float32(src_triangle_cropped), np.float32(dst_triangle_cropped))

        # Warp image
        dst_img_warped = cv2.warpAffine(src_img_cropped, transform, (dst_img_cropped.shape[1], dst_img_cropped.shape[0]), None, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101 )

        # Create mask for the triangle we want to transform
        mask = np.zeros(dst_img_cropped.shape, dtype = np.uint8)
        cv2.fillConvexPoly(mask, np.int32(dst_triangle_cropped), (1.0, 1.0, 1.0), 16, 0);

        # Delete all existing pixels at given mask
        dst_img_cropped*=1-mask
        # Add new pixels to masked area
        dst_img_cropped+=dst_img_warped*mask

if __name__ == "__main__":
    from face_landmarks import FaceLandMarkPts
    
    # Inputs
    src_img = cv2.imread("bradley_cooper.jpg")
    dst_img = cv2.imread("jim_carrey.jpg")
    src_points = np.array([(40, 27), (38, 65), (47, 115), (66, 147), (107, 166), (147, 150), (172, 118), (177, 75), (173, 26), (63, 19), (89, 30), (128, 34), (152, 27), (75, 46), (142, 46), (109, 48), (95, 96), (107, 91), (120, 97), (84, 123), (106, 117), (132, 121), (97, 137), (107, 139), (120, 135)])
    dst_points = np.array([(2, 16), (0, 60), (2, 143), (47, 181), (121, 178), (208, 181), (244, 133), (241, 87), (241, 18), (41, 15), (73, 20), (174, 16), (218, 16), (56, 23), (191, 23), (120, 48), (94, 128), (120, 122), (150, 124), (83, 174), (122, 164), (159, 173), (110, 174), (121, 174), (137, 175)])

    # Landmark detector
    landmark_obj = FaceLandMarkPts()
    src_points = landmark_obj.get_landmark_pts(src_img)
    dst_points = landmark_obj.get_landmark_pts(dst_img)

    #src_points = np.array(src_points, np.int32)
    #dst_points = np.array(dst_points, np.int32)

    # Apply transformation
    transform(src_img, src_points, dst_img, dst_points)

    # Show result
    cv2.imshow("Transformed", dst_img)

    cv2.waitKey(0)
    cv2.destroyAllWindows()