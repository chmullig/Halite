#ifndef HALITE_H
#define HALITE_H

#include <fstream>
#include <string>
#include <map>
#include <set>
#include <queue>
#include <iostream>
#include <algorithm>

#include "hlt.hpp"
#include "../rendering/OpenGL.hpp"

class Halite
{
private:
    std::vector< std::pair<std::string, float> > player_names; //float represents rendering position
	std::vector< std::vector<int> * > player_scores;
	std::vector<hlt::Map * > full_game;
	std::string present_file;
	std::map<unsigned char, Color> color_codes;
	unsigned short number_of_players;
	float defense_bonus;

	//Map rendering
	GLuint map_vertex_buffer, map_color_buffer, map_strength_buffer, map_vertex_attributes, map_vertex_shader, map_geometry_shader, map_fragment_shader, map_shader_program;
	signed short map_x_offset, map_y_offset, map_width, map_height;

	//Graph rendering
	GLuint graph_territory_vertex_buffer, graph_strength_vertex_buffer, graph_color_buffer, graph_territory_vertex_attributes, graph_strength_vertex_attributes, graph_vertex_shader, graph_fragment_shader, graph_shader_program;
	//Stats about the graph. This lets us know if we need to redo the setup for the graph.
	unsigned short graph_frame_number, graph_turn_number, graph_turn_min, graph_turn_max;
	float graph_zoom;
	unsigned int graph_max_territory, graph_max_strength;
	float territory_graph_top, territory_graph_bottom, territory_graph_left, territory_graph_right;
	float strength_graph_top, strength_graph_bottom, strength_graph_left, strength_graph_right;

	//Statistics constants:
	const float STAT_LEFT, STAT_RIGHT, STAT_BOTTOM, STAT_TOP, NAME_TEXT_HEIGHT, NAME_TEXT_OFFSET, GRAPH_TEXT_HEIGHT, GRAPH_TEXT_OFFSET, LABEL_TEXT_HEIGHT, LABEL_TEXT_OFFSET, MAP_TEXT_HEIGHT, MAP_TEXT_OFFSET;

	//Border rendering
	GLuint border_vertex_buffer, border_vertex_attributes, border_vertex_shader, border_fragment_shader, border_shader_program;

	//void loadColorCodes(std::string s);
	void setupMapGL();
	void setupMapRendering(unsigned short width, unsigned short height, signed short xOffset, signed short yOffset);
	void setupGraphGL();
	void setupGraphRendering(float zoom, short turnNumber);
	void setupBorders();
	void clearFullGame();
public:
    Halite();
	short input(GLFWwindow * window, std::string filename, unsigned short& width, unsigned short& height);
	bool isValid(std::string filename);
	void render(GLFWwindow * window, short& turnNumber, float zoom, float mouseX, float mouseY, bool mousePress, short xOffset, short yOffset);
	std::map<unsigned char, Color> getColorCodes();
	void recreateGL();
	~Halite();
};

#endif
