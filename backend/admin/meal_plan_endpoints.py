"""
Additional meal plan endpoints for admin backend
"""

from flask import request, jsonify
from datetime import datetime, timezone
import logging

def add_meal_plan_endpoints(app, supabase, verify_admin_token, sync_meal_plan_to_users):
    """Add meal plan endpoints to the admin app"""
    
    @app.route('/api/admin/meal-plans/<plan_id>', methods=['PUT', 'DELETE', 'OPTIONS'])
    def admin_meal_plan_detail(plan_id):
        if request.method == 'OPTIONS':
            return '', 200
        
        try:
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            payload = verify_admin_token(token)
            
            if not payload:
                return jsonify({'error': 'Unauthorized'}), 401
            
            if request.method == 'PUT':
                # Update meal plan
                data = request.get_json()
                
                update_data = {
                    'name': data.get('name'),
                    'description': data.get('description'),
                    'week_start': data.get('week_start'),
                    'meals': data.get('meals'),
                    'status': data.get('status'),
                    'updated_at': datetime.now(timezone.utc).isoformat()
                }
                
                # Remove None values
                update_data = {k: v for k, v in update_data.items() if v is not None}
                
                result = supabase.table('admin_meal_plans').update(update_data).eq('id', plan_id).execute()
                
                if result.data:
                    meal_plan = result.data[0]
                    try:
                        # Sync to user apps
                        sync_meal_plan_to_users(meal_plan, 'update')
                        logging.info(f'Meal plan {meal_plan["name"]} updated and synced')
                    except Exception as sync_error:
                        logging.error(f'Update sync failed: {sync_error}')
                    
                    return jsonify({
                        'message': 'Meal plan updated and synced successfully',
                        'meal_plan': meal_plan
                    }), 200
            
            elif request.method == 'DELETE':
                # Get meal plan before deletion for sync
                meal_plan_result = supabase.table('admin_meal_plans').select('*').eq('id', plan_id).execute()
                
                if meal_plan_result.data:
                    meal_plan = meal_plan_result.data[0]
                    
                    # Delete meal plan
                    supabase.table('admin_meal_plans').delete().eq('id', plan_id).execute()
                    
                    # Sync deletion to user apps
                    try:
                        sync_meal_plan_to_users(meal_plan, 'delete')
                        logging.info(f'Meal plan {meal_plan["name"]} deleted and synced')
                    except Exception as sync_error:
                        logging.error(f'Delete sync failed: {sync_error}')
                    
                    return jsonify({'message': 'Meal plan deleted and synced successfully'}), 200
                else:
                    return jsonify({'error': 'Meal plan not found'}), 404
            
        except Exception as e:
            logging.error(f'Admin meal plan detail error: {e}')
            return jsonify({'error': 'Meal plan operation failed'}), 500