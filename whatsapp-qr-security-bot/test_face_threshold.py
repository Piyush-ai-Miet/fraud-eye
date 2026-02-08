"""
Test face recognition threshold
Shows similarity scores for debugging
"""
import cv2
import numpy as np
import os
from face_recognition_simple import detect_face_opencv, compare_faces

ADMIN_FACE_DIR = 'data/admin_faces'

def test_face_similarity():
    """Test face similarity with registered faces"""
    print("=" * 60)
    print("Face Recognition Threshold Test")
    print("=" * 60)
    
    # Check if faces are registered
    if not os.path.exists(ADMIN_FACE_DIR):
        print("❌ No admin faces registered!")
        return
    
    face_files = [f for f in os.listdir(ADMIN_FACE_DIR) if f.startswith('face_') and f.endswith('.jpg')]
    
    if not face_files:
        print("❌ No face images found!")
        return
    
    print(f"\n✅ Found {len(face_files)} registered face angles:")
    for f in face_files:
        angle = f.replace('face_', '').replace('.jpg', '')
        print(f"   - {angle}")
    
    print("\n" + "=" * 60)
    print("Testing self-comparison (same face vs same face)")
    print("=" * 60)
    
    # Test each face against itself
    for face_file in face_files:
        face_path = os.path.join(ADMIN_FACE_DIR, face_file)
        angle = face_file.replace('face_', '').replace('.jpg', '')
        
        # Load face
        admin_img = cv2.imread(face_path, cv2.IMREAD_GRAYSCALE)
        success, admin_face, _ = detect_face_opencv(cv2.imencode('.jpg', admin_img)[1].tobytes())
        
        if success:
            # Compare with itself
            similarity = compare_faces(admin_face, admin_face)
            print(f"\n{angle:8s}: {similarity:.1f}% (self-comparison)")
        else:
            print(f"\n{angle:8s}: Failed to detect face")
    
    print("\n" + "=" * 60)
    print("Cross-angle comparison (different angles of same person)")
    print("=" * 60)
    
    # Load all faces
    faces = {}
    for face_file in face_files:
        face_path = os.path.join(ADMIN_FACE_DIR, face_file)
        angle = face_file.replace('face_', '').replace('.jpg', '')
        admin_img = cv2.imread(face_path, cv2.IMREAD_GRAYSCALE)
        success, admin_face, _ = detect_face_opencv(cv2.imencode('.jpg', admin_img)[1].tobytes())
        if success:
            faces[angle] = admin_face
    
    # Compare center with all other angles
    if 'center' in faces:
        print("\nComparing CENTER face with other angles:")
        for angle, face in faces.items():
            if angle != 'center':
                similarity = compare_faces(faces['center'], face)
                status = "✅ PASS" if similarity >= 75.0 else "❌ FAIL"
                print(f"  center vs {angle:6s}: {similarity:.1f}% {status}")
    
    print("\n" + "=" * 60)
    print("Current Threshold Settings:")
    print("=" * 60)
    print(f"  Similarity threshold: 65.0%")
    print(f"  Required matches: 3 out of 5 angles")
    
    # Count how many pass
    passing = sum(1 for angle, face in faces.items() if angle != 'center' and compare_faces(faces['center'], face) >= 65.0)
    total = len(faces) - 1
    
    print(f"  Your faces passing: {passing + 1}/{len(faces)} angles")  # +1 for center itself
    print(f"  Status: {'✅ WILL WORK' if passing + 1 >= 3 else '❌ TOO STRICT'}")
    print("=" * 60)

if __name__ == "__main__":
    test_face_similarity()
