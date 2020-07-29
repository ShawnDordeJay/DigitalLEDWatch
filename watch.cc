// -*- mode: c++; c-basic-offset: 2; indent-tabs-mode: nil; -*-
// Example of a clock. This is very similar to the text-example,
// except that it shows the time :)
//
// This code is public domain
// (but note, that the led-matrix library this depends on is GPL v2)

#include "led-matrix.h"
#include "graphics.h"

#include <getopt.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

using namespace rgb_matrix;

volatile bool interrupt_received = false;
static void InterruptHandler(int signo)
{
  interrupt_received = true;
}

static int usage(const char *progname)
{
  fprintf(stderr, "usage: %s [options]\n", progname);
  fprintf(stderr, "Reads text from stdin and displays it. "
                  "Empty string: clear screen\n");
  fprintf(stderr, "Options:\n");
  rgb_matrix::PrintMatrixFlags(stderr);
  fprintf(stderr,
          "\t-d <time-format>  : Default '%%H:%%M'. See strftime()\n"
          "\t-f <font-file>    : Use given font.\n"
          "\t-b <brightness>   : Sets brightness percent. Default: 100.\n"
          "\t-x <x-origin>     : X-Origin of displaying text (Default: 0)\n"
          "\t-y <y-origin>     : Y-Origin of displaying text (Default: 0)\n"
          "\t-S <spacing>      : Spacing pixels between letters (Default: 0)\n"
          "\t-C <r,g,b>        : Color. Default 255,255,0\n"
          "\t-B <r,g,b>        : Background-Color. Default 0,0,0\n"
          "\t-O <r,g,b>        : Outline-Color, e.g. to increase contrast.\n");

  return 1;
}
/*
static bool parseColor(Color *c, const char *str)
{
    return sscanf(str, "%hhu,%hhu,%hhu", &c->r, &c->g, &c->b) == 3;
}
*/
static bool FullSaturation(const Color &c)
{
  return (c.r == 0 || c.r == 255) && (c.g == 0 || c.g == 255) && (c.b == 0 || c.b == 255);
}

int main(int argc, char *argv[])
{
  RGBMatrix::Options matrix_options;
  rgb_matrix::RuntimeOptions runtime_opt;

  matrix_options.rows = 32;
  matrix_options.cols = 64;
  matrix_options.chain_length = 2;
  matrix_options.parallel = 1;
  matrix_options.pixel_mapper_config = "U-mapper";
  matrix_options.multiplexing = 0;

  runtime_opt.gpio_slowdown = 2;

  if (!rgb_matrix::ParseOptionsFromFlags(&argc, &argv,
                                         &matrix_options, &runtime_opt))
  {
    return usage(argv[0]);
  }
  const char *time_format = "%H:%M";
  const char *date_format = "%d-%m-%y";
  Color color(255, 255, 255);
  Color bg_color(0, 0, 0);
  Color outline_color(0, 0, 0);
  //bool with_outline = false;

  const char *bdf_font_file_time = "fonts/digital_time.bdf";
  const char *bdf_font_file_date = "fonts/digital_date.bdf";
  int x1_orig = 0;
  int y1_orig = 0;
  int x2_orig = 0;
  int y2_orig = 32;
  int letter_spacing = 0;
  int brightness = 50;

  rgb_matrix::Font font_time;
  if (!font_time.LoadFont(bdf_font_file_time))
  {
    fprintf(stderr, "Couldn't load font '%s'\n", bdf_font_file_time);
    return 1;
  }

  rgb_matrix::Font font_date;
  if (!font_date.LoadFont(bdf_font_file_date))
  {
    fprintf(stderr, "Couldn't load font '%s'\n", bdf_font_file_date);
    return 1;
  }

  if (brightness < 1 || brightness > 100)
  {
    fprintf(stderr, "Brightness is outside usable range.\n");
    return 1;
  }

  RGBMatrix *matrix = rgb_matrix::CreateMatrixFromOptions(matrix_options,
                                                          runtime_opt);
  if (matrix == NULL)
    return 1;

  matrix->SetBrightness(brightness);

  const bool all_extreme_colors = (brightness == 100) && FullSaturation(color) && FullSaturation(bg_color) && FullSaturation(outline_color);
  if (all_extreme_colors)
    matrix->SetPWMBits(1);

  int x1 = x1_orig;
  int y1 = y1_orig;
  int x2 = x2_orig;
  int y2 = y2_orig;

  FrameCanvas *offscreen = matrix->CreateFrameCanvas();

  char time_buffer[256];
  char date_buffer[256];
  struct timespec next_time;
  next_time.tv_sec = time(NULL);
  next_time.tv_nsec = 0;
  struct tm tm;

  signal(SIGTERM, InterruptHandler);
  signal(SIGINT, InterruptHandler);

  while (!interrupt_received)
  {
    localtime_r(&next_time.tv_sec, &tm);
    strftime(time_buffer, sizeof(time_buffer), time_format, &tm);
    strftime(date_buffer, sizeof(date_buffer), date_format, &tm);
    offscreen->Fill(bg_color.r, bg_color.g, bg_color.b);

    //get length of text to center and put color to 0 0 0
    int length = rgb_matrix::DrawText(offscreen, font_time, x1, y1,
                                      bg_color, NULL, time_buffer,
                                      letter_spacing);

    //calculate startposition for time on x axis
    x1 = (64 - length) / 2;

    rgb_matrix::DrawText(offscreen, font_time, x1, y1 + 3 + font_time.baseline(),
                         color, NULL, time_buffer,
                         letter_spacing);

    //get length of text to centralize and put color to 0 0 0
    length = DrawText(offscreen, font_date, x2, y2 + 8,
                      bg_color, NULL, date_buffer,
                      letter_spacing);

    //calculate startposition for date on x axis
    x2 = (64 - length) / 2;

    //y2+8 to center the text
    rgb_matrix::DrawText(offscreen, font_date, x2, y2 + 8 + font_date.baseline(),
                         color, NULL, date_buffer,
                         letter_spacing);

    // Wait until we're ready to show it.
    clock_nanosleep(CLOCK_REALTIME, TIMER_ABSTIME, &next_time, NULL);

    // Atomic swap with double buffer
    offscreen = matrix->SwapOnVSync(offscreen);

    next_time.tv_sec += 1;
  }

  // Finished. Shut down the RGB matrix.
  matrix->Clear();
  delete matrix;

  write(STDOUT_FILENO, "\n", 1); // Create a fresh new line after ^C on screen
  return 0;
}
