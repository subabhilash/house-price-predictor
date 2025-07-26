from app import create_app

def test_templates():
    """Test if all templates are properly created"""
    app = create_app('development')
    
    with app.app_context():
        try:
            # Test if Flask can find all templates
            from flask import render_template_string
            
            templates_to_check = [
                'base.html',
                'index.html', 
                'login.html',
                'signup.html'
            ]
            
            print("🔍 Checking templates...")
            
            for template in templates_to_check:
                try:
                    app.jinja_env.get_template(template)
                    print(f"✅ {template} - Found")
                except Exception as e:
                    print(f"❌ {template} - Error: {e}")
            
            # Check CSS file
            import os
            css_path = os.path.join('static', 'css', 'style.css')
            if os.path.exists(css_path):
                print("✅ style.css - Found")
            else:
                print("❌ style.css - Not found")
            
            print("\n🎉 Template setup complete!")
            print("📋 Next steps:")
            print("   1. Copy your trained ML model to the models/ folder")
            print("   2. Run the Flask application")
            print("   3. Test the web interface")
            
            return True
            
        except Exception as e:
            print(f"❌ Template test failed: {e}")
            return False

if __name__ == "__main__":
    test_templates()
