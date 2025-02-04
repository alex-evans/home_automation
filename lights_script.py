
from datetime import datetime
from dotenv import load_dotenv
import json
import os
import requests
import logging

load_dotenv()

HOME_ASSISTANT_TOKEN = os.getenv("HOME_ASSISTANT_TOKEN")
HOME_ASSISTANT_URL = os.getenv("HOME_ASSISTANT_URL", "http://localhost:8123")


logger = logging.getLogger(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Lights')
logging.basicConfig(level=logging.INFO)


######################
# Get lights
######################

def get_all_lights():
    api_states_url = f'{HOME_ASSISTANT_URL}api/states'
    headers = {
        "Authorization": f"Bearer {HOME_ASSISTANT_TOKEN}",
        "content-type": "application/json",
    }
    logger.info(f'Getting all lights from {api_states_url}')
    response = requests.get(api_states_url, headers=headers)
    if response.status_code != 200:
        logger.error('Houston we have a problem!')
        logger.error(f"Error: {response}")
        raise Exception(f"Error: {response.status_code}")
    
    logger.info(f'Lights response: {response}')
    entities = response.json()
    lights = []
    for entity in entities:
        if entity["entity_id"].startswith("light."):
            lights.append(entity['entity_id'])
    
    return sorted(lights)


######################
# Group Lights
######################

def get_entity_state(entity_id):
    api_state_url = f'{HOME_ASSISTANT_URL}api/states/{entity_id}'
    headers = {
        "Authorization": HOME_ASSISTANT_TOKEN,
        "content-type": "application/json",
    }

    response = requests.get(api_state_url, headers=headers)

    if response.status_code != 200:
        logger.error(f"Error: {response.json()}")
        raise Exception(f"Error: {response.status_code}")
    
    return response.json()


def group_lights_by_capability(lights):
    color_temp_lights = []
    brightness_lights = []
    other_lights = []

    for light in lights:
        state = get_entity_state(light)
        if not state:
            continue

        attrs = state['attributes']
        if 'supported_color_modes' in attrs:
            if 'color_temp' in attrs['supported_color_modes']:
                color_temp_lights.append(light)
            elif 'brightness' in attrs['supported_color_modes']:
                brightness_lights.append(light)
            else:
                other_lights.append(light)
    
    return {
        'color_temp': color_temp_lights,
        'brightness': brightness_lights,
        'other': other_lights,
    }


######################
# Analyze Lights
######################

def get_adaptive_lighting_switch_state(group_name):
    switch_id = f'switch.adaptive_lighting_{group_name.lower()}'
    state = get_entity_state(switch_id)
    if state:
        logger.info(f'Adaptive switch {switch_id} full state: {json.dumps(state, indent=2)}')
        return state
    logger.error(f'Adaptive switch {switch_id} not found')
    return None


def get_adaptive_lighting_switch_config(group_name):
    switch_state = get_adaptive_lighting_switch_state(group_name)
    if not switch_state:
        logger.error(f'Adaptive switch {switch_state["entity_id"]} not found')
        return {}

    if 'attributes' not in switch_state:
        logger.error(f'Adaptive switch {switch_state["entity_id"]} has no attributes')
        return {}
    
    logger.info(f'Adaptive Lighting Switch: {switch_state["state"]}')
    logger.info(f'Last changed: {switch_state.get("last_changed", "unknown")}')
    logger.info(f'Attributes: {json.dumps(switch_state["attributes"], indent=2)}')
    return switch_state['attributes']
    

def track_brightness_stats(lights):
    brightness_stats = {
        'min': float('inf'),
        'max': float('-inf'),
        'total': 0,
        'count': 0
    }

    for light in lights:
        state = get_entity_state(light)
        if not state:
            logger.warning(f'{light}: Not found or offline')
            continue

        attrs = state['attributes']
        status = []
        capabilities = []

        



def analyze_current_state(lights, group_name):
    logger.info(f'=== {group_name.capitalize()} Lights Analysis ===')
    logger.info(f'Total {group_name.capitalize()} Lights: {len(lights)}')

    switch_state = get_adaptive_lighting_switch_config(group_name)

    brightness_stats = track_brightness_stats(lights)


######################
# Main
######################

def main():
    all_lights = get_all_lights()
    logger.info(f'=== All Lights Analysis ===')
    logger.info(f'Total Lights: {len(all_lights)}')

    grouped_lights = group_lights_by_capability(all_lights)

    for group_name, lights in grouped_lights.items():
        if not lights:
            continue
        analyze_current_state(lights, group_name)


if __name__ == "__main__":
    main()