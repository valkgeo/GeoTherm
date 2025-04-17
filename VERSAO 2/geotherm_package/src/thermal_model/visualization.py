"""
GeoTherm - Módulo de Visualização

Este módulo fornece funções para visualizar os resultados do modelamento térmico.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

def visualize_thermal_field(model, output_dir=None):
    """
    Cria visualizações 2D do campo térmico.
    
    Parâmetros:
        model: Modelo térmico
        output_dir (str): Diretório para salvar as visualizações
    """
    # Criar diretório se não existir
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Obter fatias centrais
    slice_xy = model.get_slice('z', model.nz // 2)
    slice_xz = model.get_slice('y', model.ny // 2)
    slice_yz = model.get_slice('x', model.nx // 2)
    
    # Configurar mapa de cores personalizado (vermelho para altas temperaturas)
    colors = [(0, 0, 1), (1, 1, 1), (1, 0, 0)]  # azul -> branco -> vermelho
    cmap = LinearSegmentedColormap.from_list('thermal', colors, N=256)
    
    # Configurar limites de temperatura
    vmin = model.background_temperature
    vmax = model.magma_temperature
    
    # Criar figura para fatia XY
    plt.figure(figsize=(10, 8))
    plt.imshow(slice_xy.T, origin='lower', cmap=cmap, vmin=vmin, vmax=vmax)
    plt.colorbar(label='Temperatura (°C)')
    plt.title(f'Corte XY (Z = {model.nz // 2}) - t = {model.time:.2e} s')
    plt.xlabel('X')
    plt.ylabel('Y')
    
    # Salvar ou mostrar
    if output_dir:
        plt.savefig(os.path.join(output_dir, f'slice_xy_t{model.time:.2e}.png'), dpi=300)
        plt.close()
    else:
        plt.show()
    
    # Criar figura para fatia XZ
    plt.figure(figsize=(10, 8))
    plt.imshow(slice_xz.T, origin='lower', cmap=cmap, vmin=vmin, vmax=vmax)
    plt.colorbar(label='Temperatura (°C)')
    plt.title(f'Corte XZ (Y = {model.ny // 2}) - t = {model.time:.2e} s')
    plt.xlabel('X')
    plt.ylabel('Z')
    
    # Salvar ou mostrar
    if output_dir:
        plt.savefig(os.path.join(output_dir, f'slice_xz_t{model.time:.2e}.png'), dpi=300)
        plt.close()
    else:
        plt.show()
    
    # Criar figura para fatia YZ
    plt.figure(figsize=(10, 8))
    plt.imshow(slice_yz.T, origin='lower', cmap=cmap, vmin=vmin, vmax=vmax)
    plt.colorbar(label='Temperatura (°C)')
    plt.title(f'Corte YZ (X = {model.nx // 2}) - t = {model.time:.2e} s')
    plt.xlabel('Y')
    plt.ylabel('Z')
    
    # Salvar ou mostrar
    if output_dir:
        plt.savefig(os.path.join(output_dir, f'slice_yz_t{model.time:.2e}.png'), dpi=300)
        plt.close()
    else:
        plt.show()

def plot_temperature_history(model, output_file=None):
    """
    Plota o histórico de temperatura.
    
    Parâmetros:
        model: Modelo térmico
        output_file (str): Arquivo para salvar o gráfico
    """
    # Verificar se há pontos de histórico
    if not model.history_points:
        print("Nenhum ponto de histórico definido")
        return
    
    # Criar figura
    plt.figure(figsize=(12, 8))
    
    # Plotar histórico para cada ponto
    for point, history in model.temperature_history.items():
        times = [t for t, _ in history]
        temps = [temp for _, temp in history]
        plt.plot(times, temps, '-o', label=f'Ponto {point}')
    
    # Configurar gráfico
    plt.title('Evolução de Temperatura')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Temperatura (°C)')
    plt.xscale('log')
    plt.grid(True)
    plt.legend()
    
    # Salvar ou mostrar
    if output_file:
        plt.savefig(output_file, dpi=300)
        plt.close()
    else:
        plt.show()

def plot_isotherm_evolution(temperature_data, isotherm_value, output_file=None):
    """
    Plota a evolução de uma isoterma específica.
    
    Parâmetros:
        temperature_data (list): Lista de arrays de temperatura
        isotherm_value (float): Valor da isoterma (°C)
        output_file (str): Arquivo para salvar o gráfico
    """
    # Verificar se há dados
    if not temperature_data:
        print("Nenhum dado de temperatura fornecido")
        return
    
    # Obter dimensões
    nx, ny, nz = temperature_data[0].shape
    
    # Criar figura
    plt.figure(figsize=(12, 8))
    
    # Obter fatia central
    slice_idx = nz // 2
    
    # Configurar mapa de cores
    cmap = plt.cm.viridis
    
    # Plotar contornos para cada ponto de tempo
    for i, temp in enumerate(temperature_data):
        slice_xy = temp[:, :, slice_idx]
        
        # Plotar contorno da isoterma
        cs = plt.contour(slice_xy.T, levels=[isotherm_value], colors=[cmap(i / len(temperature_data))])
        
        # Adicionar rótulo
        fmt = {cs.levels[0]: f't{i}'}
        plt.clabel(cs, cs.levels, inline=True, fmt=fmt, fontsize=10)
    
    # Configurar gráfico
    plt.title(f'Evolução da Isoterma {isotherm_value}°C')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.grid(True)
    
    # Salvar ou mostrar
    if output_file:
        plt.savefig(output_file, dpi=300)
        plt.close()
    else:
        plt.show()

def visualize_3d_with_pyvista(model, output_file=None):
    """
    Cria visualização 3D usando PyVista.
    
    Parâmetros:
        model: Modelo térmico
        output_file (str): Arquivo para salvar a visualização
    """
    try:
        import pyvista as pv
        
        # Criar malha estruturada
        grid = pv.StructuredGrid(model.x_grid, model.y_grid, model.z_grid)
        
        # Adicionar temperatura como escalar
        grid.point_data["Temperature"] = model.temperature.flatten(order="F")
        
        # Criar plotter
        plotter = pv.Plotter(off_screen=output_file is not None)
        
        # Adicionar malha com mapa de cores
        plotter.add_mesh(grid, scalars="Temperature", cmap="coolwarm",
                        scalar_bar_args={"title": "Temperatura (°C)"})
        
        # Adicionar planos de corte
        plotter.add_mesh_clip_plane(grid, normal="x", value=model.nx // 2)
        
        # Configurar câmera
        plotter.camera_position = [(3, 3, 3), (0, 0, 0), (0, 0, 1)]
        plotter.camera.zoom(1.5)
        
        # Salvar ou mostrar
        if output_file:
            plotter.screenshot(output_file, transparent_background=True)
            plotter.close()
        else:
            plotter.show()
            
    except ImportError:
        print("PyVista não está instalado. Use 'pip install pyvista' para instalar.")

def create_animation(model_history, output_file=None):
    """
    Cria animação da evolução temporal.
    
    Parâmetros:
        model_history (list): Lista de modelos térmicos em diferentes tempos
        output_file (str): Arquivo para salvar a animação
    """
    try:
        from matplotlib.animation import FuncAnimation
        
        # Verificar se há dados
        if not model_history:
            print("Nenhum histórico de modelo fornecido")
            return
        
        # Obter dimensões
        nx, ny, nz = model_history[0].temperature.shape
        
        # Configurar mapa de cores
        colors = [(0, 0, 1), (1, 1, 1), (1, 0, 0)]  # azul -> branco -> vermelho
        cmap = LinearSegmentedColormap.from_list('thermal', colors, N=256)
        
        # Configurar limites de temperatura
        vmin = model_history[0].background_temperature
        vmax = model_history[0].magma_temperature
        
        # Criar figura
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Função de atualização para animação
        def update(frame):
            ax.clear()
            
            # Obter fatia central
            slice_xy = model_history[frame].get_slice('z', nz // 2)
            
            # Plotar fatia
            im = ax.imshow(slice_xy.T, origin='lower', cmap=cmap, vmin=vmin, vmax=vmax)
            
            # Adicionar barra de cores se for o primeiro quadro
            if frame == 0:
                fig.colorbar(im, ax=ax, label='Temperatura (°C)')
            
            # Configurar título e rótulos
            ax.set_title(f'Evolução Térmica - t = {model_history[frame].time:.2e} s')
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            
            return [im]
        
        # Criar animação
        anim = FuncAnimation(fig, update, frames=len(model_history), interval=200, blit=True)
        
        # Salvar ou mostrar
        if output_file:
            anim.save(output_file, writer='pillow', fps=5)
            plt.close()
        else:
            plt.show()
            
    except ImportError:
        print("Matplotlib animation não está disponível.")
