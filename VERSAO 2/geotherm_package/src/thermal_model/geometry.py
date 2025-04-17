"""
GeoTherm - Módulo de Geometria

Este módulo fornece funções para criar diferentes geometrias de intrusão.
"""

import numpy as np

def create_planar_intrusion(x_grid, y_grid, z_grid, x0, y0, z0, width, height, thickness):
    """
    Cria uma intrusão planar (sill).
    
    Parâmetros:
        x_grid, y_grid, z_grid (ndarray): Grades de coordenadas
        x0, y0, z0 (float): Coordenadas do canto inferior esquerdo da intrusão
        width (float): Largura da intrusão (direção x)
        height (float): Comprimento da intrusão (direção y)
        thickness (float): Espessura da intrusão (direção z)
    
    Retorna:
        ndarray: Máscara booleana 3D indicando a região da intrusão
    """
    # Criar máscara
    mask = ((x_grid >= x0) & (x_grid <= x0 + width) & 
            (y_grid >= y0) & (y_grid <= y0 + height) & 
            (z_grid >= z0) & (z_grid <= z0 + thickness))
    
    return mask

def create_cylindrical_intrusion(x_grid, y_grid, z_grid, x0, y0, z0, radius, height):
    """
    Cria uma intrusão cilíndrica (dique).
    
    Parâmetros:
        x_grid, y_grid, z_grid (ndarray): Grades de coordenadas
        x0, y0, z0 (float): Coordenadas do centro da base do cilindro
        radius (float): Raio do cilindro
        height (float): Altura do cilindro
    
    Retorna:
        ndarray: Máscara booleana 3D indicando a região da intrusão
    """
    # Calcular distância radial ao eixo do cilindro
    r = np.sqrt((x_grid - x0)**2 + (y_grid - y0)**2)
    
    # Criar máscara
    mask = (r <= radius) & (z_grid >= z0) & (z_grid <= z0 + height)
    
    return mask

def create_spherical_intrusion(x_grid, y_grid, z_grid, x0, y0, z0, radius):
    """
    Cria uma intrusão esférica (plúton).
    
    Parâmetros:
        x_grid, y_grid, z_grid (ndarray): Grades de coordenadas
        x0, y0, z0 (float): Coordenadas do centro da esfera
        radius (float): Raio da esfera
    
    Retorna:
        ndarray: Máscara booleana 3D indicando a região da intrusão
    """
    # Calcular distância ao centro da esfera
    r = np.sqrt((x_grid - x0)**2 + (y_grid - y0)**2 + (z_grid - z0)**2)
    
    # Criar máscara
    mask = (r <= radius)
    
    return mask

def create_complex_intrusion(x_grid, y_grid, z_grid, components):
    """
    Cria uma intrusão complexa combinando múltiplas geometrias.
    
    Parâmetros:
        x_grid, y_grid, z_grid (ndarray): Grades de coordenadas
        components (list): Lista de dicionários com parâmetros para cada componente
    
    Retorna:
        ndarray: Máscara booleana 3D indicando a região da intrusão
    """
    # Inicializar máscara vazia
    mask = np.zeros_like(x_grid, dtype=bool)
    
    # Adicionar cada componente
    for comp in components:
        if comp['type'] == 'planar':
            comp_mask = create_planar_intrusion(
                x_grid, y_grid, z_grid,
                comp['x0'], comp['y0'], comp['z0'],
                comp['width'], comp['height'], comp['thickness']
            )
        elif comp['type'] == 'cylindrical':
            comp_mask = create_cylindrical_intrusion(
                x_grid, y_grid, z_grid,
                comp['x0'], comp['y0'], comp['z0'],
                comp['radius'], comp['height']
            )
        elif comp['type'] == 'spherical':
            comp_mask = create_spherical_intrusion(
                x_grid, y_grid, z_grid,
                comp['x0'], comp['y0'], comp['z0'],
                comp['radius']
            )
        else:
            continue
        
        # Combinar com máscara existente
        mask = np.logical_or(mask, comp_mask)
    
    return mask
