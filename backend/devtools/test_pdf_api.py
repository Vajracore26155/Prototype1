"""
Test API endpoint for PDF report generation
"""
import requests

def test_pdf_api_endpoint():
    """Test the PDF report API endpoint"""
    
    base_url = "http://localhost:8000"
    audit_id = "AUD-998777"
    
    print(f"Testing API endpoint: GET /api/audits/{audit_id}/report")
    print("-" * 60)
    
    try:
        # Test the endpoint
        response = requests.get(
            f"{base_url}/api/audits/{audit_id}/report",
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Content-Disposition: {response.headers.get('Content-Disposition')}")
        print(f"Content-Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            # Save the PDF
            output_file = f"api_test_report_{audit_id}.pdf"
            with open(output_file, 'wb') as f:
                f.write(response.content)
            
            print(f"\n✓ PDF downloaded successfully!")
            print(f"✓ Saved to: {output_file}")
            return True
        else:
            print(f"\n✗ API returned error: {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n⚠ Backend server is not running!")
        print("Start the server with: uvicorn app.main:app --reload")
        return None
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("PDF REPORT API ENDPOINT TEST")
    print("=" * 60)
    print()
    
    result = test_pdf_api_endpoint()
    
    print()
    print("=" * 60)
    
    if result is None:
        print("⚠ TEST SKIPPED - Server not running")
    elif result:
        print("✓ TEST PASSED!")
    else:
        print("✗ TEST FAILED!")
    
    print("=" * 60)
