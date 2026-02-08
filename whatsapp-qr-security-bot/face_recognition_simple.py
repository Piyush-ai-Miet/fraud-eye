"""
Multi-Angle Face Recognition using OpenCV
Captures face from multiple angles for better accuracy
"""
import cv2
import numpy as np
import os
import json

ADMIN_FACE_DIR = 'data/admin_faces'
FACE_DATA_FILE = 'data/admin_face_data.json'

def detect_face_opencv(image_data):
    """Detect face in image using OpenCV"""
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return False, None, "Invalid image"
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply histogram equalization for better detection in poor lighting
        gray = cv2.equalizeHist(gray)
        
        # Load face cascade
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Detect faces with MORE LENIENT parameters
        # scaleFactor: 1.1 (was 1.3) - smaller = more sensitive
        # minNeighbors: 3 (was 5) - smaller = more detections
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30))
        
        if len(faces) == 0:
            return False, None, "No face detected"
        
        # Get first face
        (x, y, w, h) = faces[0]
        face_img = gray[y:y+h, x:x+w]
        
        # Resize to standard size
        face_img = cv2.resize(face_img, (100, 100))
        
        return True, face_img, "Face detected"
        
    except Exception as e:
        return False, None, f"Error: {str(e)}"

def register_admin_face_multi(image_data, angle_name):
    """Register admin face from specific angle (center, left, right, up, down)"""
    success, face_img, message = detect_face_opencv(image_data)
    
    if not success:
        return False, message
    
    try:
        # Create directory for face profiles
        os.makedirs(ADMIN_FACE_DIR, exist_ok=True)
        
        # Save face image for this angle
        face_path = os.path.join(ADMIN_FACE_DIR, f'face_{angle_name}.jpg')
        
        # Convert face_img to BGR for saving
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        cv2.imwrite(face_path, img)
        
        # Save face features
        face_features = {
            'mean': float(np.mean(face_img)),
            'std': float(np.std(face_img)),
            'shape': face_img.shape,
            'histogram': cv2.calcHist([face_img], [0], None, [256], [0, 256]).flatten().tolist()[:50]
        }
        
        # Load or create face data file
        if os.path.exists(FACE_DATA_FILE):
            with open(FACE_DATA_FILE, 'r') as f:
                all_faces = json.load(f)
        else:
            all_faces = {}
        
        all_faces[angle_name] = face_features
        
        with open(FACE_DATA_FILE, 'w') as f:
            json.dump(all_faces, f, indent=2)
        
        return True, f"Face angle '{angle_name}' registered successfully"
        
    except Exception as e:
        return False, f"Error saving face: {str(e)}"

def compare_faces(face1, face2):
    """Compare two face images using multiple methods for higher accuracy"""
    try:
        # Method 1: Histogram comparison
        hist1 = cv2.calcHist([face1], [0], None, [256], [0, 256])
        hist2 = cv2.calcHist([face2], [0], None, [256], [0, 256])
        hist_similarity = float(cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL))
        
        # Method 2: Template matching
        result = cv2.matchTemplate(face1, face2, cv2.TM_CCOEFF_NORMED)
        template_similarity = float(result[0][0])
        
        # Method 3: Structural similarity (pixel-wise comparison)
        # Normalize both images
        face1_norm = cv2.normalize(face1, None, 0, 255, cv2.NORM_MINMAX)
        face2_norm = cv2.normalize(face2, None, 0, 255, cv2.NORM_MINMAX)
        
        # Calculate mean squared error
        mse = np.mean((face1_norm - face2_norm) ** 2)
        max_mse = 255 ** 2  # Maximum possible MSE
        structural_similarity = 1 - (mse / max_mse)
        
        # Weighted average of all methods (histogram has highest weight)
        final_similarity = (
            hist_similarity * 0.5 +      # 50% weight
            template_similarity * 0.3 +   # 30% weight
            structural_similarity * 0.2   # 20% weight
        )
        
        # Convert to percentage (0-100)
        similarity_score = final_similarity * 100
        
        return float(similarity_score)
        
    except Exception as e:
        print(f"Comparison error: {e}")
        return 0.0

def verify_face(image_data):
    """Verify face against registered admin faces - FAST verification for Render (only 2 angles)"""
    # Check if admin faces are registered
    if not os.path.exists(ADMIN_FACE_DIR):
        return False, "Admin face not registered. Please register first.", 0
    
    # Detect face in current image
    success, current_face, message = detect_face_opencv(image_data)
    
    if not success:
        return False, message, 0
    
    try:
        # OPTIMIZATION: Only check CENTER and LEFT angles for SPEED (Render optimization)
        priority_angles = ['center', 'left']  # Fastest verification - only 2 angles
        
        angle_scores = {}
        matches_above_threshold = 0
        threshold = 45.0  # Even MORE LENIENT for Render (was 50.0)
        
        for angle_name in priority_angles:
            face_path = os.path.join(ADMIN_FACE_DIR, f'face_{angle_name}.jpg')
            
            if not os.path.exists(face_path):
                continue
            
            admin_img = cv2.imread(face_path, cv2.IMREAD_GRAYSCALE)
            if admin_img is None:
                continue
                
            success, admin_face, _ = detect_face_opencv(cv2.imencode('.jpg', admin_img)[1].tobytes())
            
            if success:
                similarity = compare_faces(admin_face, current_face)
                angle_scores[angle_name] = similarity
                
                if similarity >= threshold:
                    matches_above_threshold += 1
                    # FAST EXIT: If one angle matches, accept immediately (for speed)
                    print(f"[FACE] Quick match on {angle_name}: {similarity:.1f}%")
                    return True, f"Face matched! ({angle_name}: {similarity:.1f}%)", similarity
        
        # If no quick match, check best score
        if angle_scores:
            best_angle = max(angle_scores, key=angle_scores.get)
            best_similarity = angle_scores[best_angle]
            
            if best_similarity >= threshold:
                return True, f"Face matched! (Best: {best_similarity:.1f}%)", best_similarity
            else:
                return False, f"Face not matched. Best: {best_similarity:.1f}% (need {threshold}%)", best_similarity
        else:
            return False, "No face angles found for comparison", 0
            
    except Exception as e:
        return False, f"Verification error: {str(e)}", 0

def get_registration_status():
    """Check which angles are registered - Now 4 angles instead of 5"""
    if not os.path.exists(ADMIN_FACE_DIR):
        return {}
    
    angles = ['center', 'left', 'right', 'up']  # Removed 'down' - only 4 angles now
    status = {}
    
    for angle in angles:
        face_path = os.path.join(ADMIN_FACE_DIR, f'face_{angle}.jpg')
        status[angle] = os.path.exists(face_path)
    
    return status

if __name__ == "__main__":
    print("OpenCV Face Recognition Test")
    print("=" * 50)
    
    # Test if OpenCV is working
    try:
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        print("✅ OpenCV face detection ready")
    except Exception as e:
        print(f"❌ OpenCV error: {e}")
