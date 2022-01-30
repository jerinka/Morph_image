import cv2
import numpy as np
import time

def show(img, win='img', time=30):
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    cv2.imshow(win, img)
    cv2.waitKey(time)

def morph(bg_img, bg_pts, fg_img, fg_pts):
    """crop fg_img using fg_pts, moprh and place it on bg_img"""
    img1 = fg_img
    img2 = bg_img
    landmarks_points1 = fg_pts
    landmarks_points2 = bg_pts

    points = np.array(landmarks_points1, np.int32)
    convexhull = cv2.convexHull(points)
    cv2.fillConvexPoly(mask, convexhull, 255)

    face_image_1 = cv2.bitwise_and(img1, img1, mask=mask)
    show(face_image_1, win='face_image_1', time=30)
    img1_copy = img1.copy()

    # Delaunay triangulation
    rect = cv2.boundingRect(convexhull)
    subdiv = cv2.Subdiv2D(rect)
    #import pdb;pdb.set_trace()
    
    subdiv.insert(landmarks_points1)
    triangles = subdiv.getTriangleList()
    triangles = np.array(triangles, dtype=np.int32)

    indexes_triangles = []
    for t in triangles:
        pt1 = (t[0], t[1])
        pt2 = (t[2], t[3])
        pt3 = (t[4], t[5])
        index_pt1 = np.where((points == pt1).all(axis=1))[0][0]
        index_pt2 = np.where((points == pt2).all(axis=1))[0][0]
        index_pt3 = np.where((points == pt3).all(axis=1))[0][0]

        if index_pt1 is not None and index_pt2 is not None and index_pt3 is not None:
            triangle = [index_pt1, index_pt2, index_pt3]
            indexes_triangles.append(triangle)
            
            pts =  [pt1,pt2,pt3]
            pts = np.array(pts, np.int32)
            #import pdb;pdb.set_trace()
            cv2.polylines(img1_copy,[pts], False, (255, 0, 0), 3)
    show(img1_copy, win='img1_copy_poly', time=30)

    # Face 2

    points2 = np.array(landmarks_points2, np.int32)
    convexhull2 = cv2.convexHull(points2)

    height, width, channels = img2.shape
    img2_new_face = np.zeros((height, width, channels), np.uint8)

    lines_space_mask = np.zeros_like(img1_gray)
    lines_space_new_face = np.zeros_like(img2)
    # Triangulation of both faces
    for triangle_index in indexes_triangles:
        # Triangulation of the first face
        tr1_pt1 = landmarks_points1[triangle_index[0]]
        tr1_pt2 = landmarks_points1[triangle_index[1]]
        tr1_pt3 = landmarks_points1[triangle_index[2]]
        triangle1 = np.array([tr1_pt1, tr1_pt2, tr1_pt3], np.int32)

        rect1 = cv2.boundingRect(triangle1)
        (x, y, w, h) = rect1
        cropped_triangle = img1[y: y + h, x: x + w]
        cropped_tr1_mask = np.zeros((h, w), np.uint8)

        points = np.array([[tr1_pt1[0] - x, tr1_pt1[1] - y],
                        [tr1_pt2[0] - x, tr1_pt2[1] - y],
                        [tr1_pt3[0] - x, tr1_pt3[1] - y]], np.int32)

        cv2.fillConvexPoly(cropped_tr1_mask, points, 255)

        # Lines space
        cv2.line(lines_space_mask, tr1_pt1, tr1_pt2, 255)
        cv2.line(lines_space_mask, tr1_pt2, tr1_pt3, 255)
        cv2.line(lines_space_mask, tr1_pt1, tr1_pt3, 255)
        lines_space = cv2.bitwise_and(img1, img1, mask=lines_space_mask)

        # Triangulation of second face
        tr2_pt1 = landmarks_points2[triangle_index[0]]
        tr2_pt2 = landmarks_points2[triangle_index[1]]
        tr2_pt3 = landmarks_points2[triangle_index[2]]
        triangle2 = np.array([tr2_pt1, tr2_pt2, tr2_pt3], np.int32)


        rect2 = cv2.boundingRect(triangle2)
        (x, y, w, h) = rect2

        cropped_tr2_mask = np.zeros((h, w), np.uint8)

        points2 = np.array([[tr2_pt1[0] - x, tr2_pt1[1] - y],
                            [tr2_pt2[0] - x, tr2_pt2[1] - y],
                            [tr2_pt3[0] - x, tr2_pt3[1] - y]], np.int32)

        cv2.fillConvexPoly(cropped_tr2_mask, points2, 255)

        # Warp triangles
        points = np.float32(points)
        points2 = np.float32(points2)
        M = cv2.getAffineTransform(points, points2)
        warped_triangle = cv2.warpAffine(cropped_triangle, M, (w, h))
        warped_triangle = cv2.bitwise_and(warped_triangle, warped_triangle, mask=cropped_tr2_mask)

        # Reconstructing destination face
        img2_new_face_rect_area = img2_new_face[y: y + h, x: x + w]
        img2_new_face_rect_area_gray = cv2.cvtColor(img2_new_face_rect_area, cv2.COLOR_BGR2GRAY)
        _, mask_triangles_designed = cv2.threshold(img2_new_face_rect_area_gray, 1, 255, cv2.THRESH_BINARY_INV)
        warped_triangle = cv2.bitwise_and(warped_triangle, warped_triangle, mask=mask_triangles_designed)

        img2_new_face_rect_area = cv2.add(img2_new_face_rect_area, warped_triangle)
        img2_new_face[y: y + h, x: x + w] = img2_new_face_rect_area


    # Face swapped (putting 1st face into 2nd face)
    img2_face_mask = np.zeros_like(img2_gray)
    img2_head_mask = cv2.fillConvexPoly(img2_face_mask, convexhull2, 255)
    img2_face_mask = cv2.bitwise_not(img2_head_mask)


    img2_head_noface = cv2.bitwise_and(img2, img2, mask=img2_face_mask)
    result = cv2.add(img2_head_noface, img2_new_face)

    (x, y, w, h) = cv2.boundingRect(convexhull2)
    center_face2 = (int((x + x + w) / 2), int((y + y + h) / 2))

    seamlessclone = cv2.seamlessClone(result, img2, img2_head_mask, center_face2, cv2.NORMAL_CLONE)

    return seamlessclone

if __name__=="__main__":
    from face_landmarks import FaceLandMarkPts
    
    img1 = cv2.imread("bradley_cooper.jpg")
    img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    mask = np.zeros_like(img1_gray)
    img2 = cv2.imread("jim_carrey.jpg")
    img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    show(img1, win='img1', time=30)
    show(img2, win='img2', time=30)

    # Landmark detector
    landmark_obj = FaceLandMarkPts()
    landmarks_points1 = landmark_obj.get_landmark_pts(img1)
    landmarks_points2 = landmark_obj.get_landmark_pts(img2)

    seamlessclone = morph(bg_img=img2, bg_pts=landmarks_points2, fg_img=img1, fg_pts=landmarks_points1)

    cv2.imshow("seamlessclone", seamlessclone)
    cv2.waitKey(0)
    cv2.destroyAllWindows()