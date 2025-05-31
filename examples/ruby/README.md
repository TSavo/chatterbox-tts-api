# Chatterbox TTS API v3.0 - Ruby Examples

Examples for using the enhanced Chatterbox TTS API with Ruby.
Features new job tracking, queue system, and multiple output formats.

## Prerequisites

1. Make sure the API is running: `docker-compose up -d`
2. Install required gems: `gem install httparty base64`

## Quick Example

```ruby
require 'httparty'
require 'base64'
require 'json'

class ChatterboxClient
  include HTTParty
  base_uri 'http://localhost:8000'
  
  def initialize
    @options = {
      headers: {
        'Content-Type' => 'application/json'
      },
      timeout: 60  # Increased for queue processing
    }
  end
  
  def check_health
    response = self.class.get('/health', @options)
    
    if response.success?
      puts "✅ API is healthy!"
      health_data = response.parsed_response
      puts "   Device: #{health_data['device'] || 'unknown'}"
      puts "   GPU Available: #{health_data['gpu_available'] || false}"
      puts "   Sample Rate: #{health_data['sample_rate'] || 'unknown'}"
      true
    else
      puts "❌ API health check failed: #{response.code}"
      false
    end
  rescue => e
    puts "❌ Cannot connect to API: #{e.message}"
    puts "Make sure to run: docker-compose up -d"
    false
  end
  
  # NEW in v3.0: Queue status checking
  def check_queue_status
    response = self.class.get('/queue/status', @options)
    
    if response.success?
      queue_data = response.parsed_response
      puts "📊 Queue Status:"
      puts "   Queue Size: #{queue_data['queue_size'] || 0}"
      puts "   Active Jobs: #{queue_data['active_jobs'] || 0}"
      puts "   Total Processed: #{queue_data['total_jobs_processed'] || 0}"
      queue_data
    else
      puts "❌ Queue status check failed: #{response.code}"
      nil
    end
  rescue => e
    puts "❌ Cannot get queue status: #{e.message}"
    nil
  end
  
  # NEW in v3.0: Job status checking
  def check_job_status(job_id)
    response = self.class.get("/job/#{job_id}/status", @options)
    
    if response.success?
      response.parsed_response
    else
      puts "❌ Job status check failed: #{response.code}"
      nil
    end
  rescue => e
    puts "❌ Cannot get job status: #{e.message}"
    nil
  end
  
  def generate_speech(text, options = {})
    request_data = {
      text: text,
      exaggeration: options[:exaggeration] || 0.7,
      cfg_weight: options[:cfg_weight] || 0.6,
      temperature: options[:temperature] || 1.0,
      output_format: options[:output_format] || 'wav',  # NEW: Format support
      return_base64: options[:return_base64] || true
    }
    
    response = self.class.post('/tts', @options.merge(body: request_data.to_json))
    
    if response.success?
      response.parsed_response
    else
      { 'success' => false, 'message' => "HTTP #{response.code}: #{response.body}" }
    end
  rescue => e
    { 'success' => false, 'message' => e.message }
  end
  
  def voice_clone(text, audio_file_path, options = {})
    unless File.exist?(audio_file_path)
      return { 'success' => false, 'message' => "Audio file not found: #{audio_file_path}" }
    end
    
    request_options = {
      body: {
        text: text,
        exaggeration: options[:exaggeration] || 0.6,
        cfg_weight: options[:cfg_weight] || 0.7,
        temperature: options[:temperature] || 0.9,
        output_format: options[:output_format] || 'wav',  # NEW: Format support
        return_base64: options[:return_base64] || true,
        audio_file: File.open(audio_file_path)
      },
      timeout: 60
    }
    
    response = self.class.post('/voice-clone', request_options)
    
    if response.success?
      if response.headers['content-type']&.include?('audio/')
        { 'success' => true, 'audio_data' => response.body }
      else
        response.parsed_response
      end
    else
      { 'success' => false, 'message' => "HTTP #{response.code}: #{response.body}" }
    end
  rescue => e
    { 'success' => false, 'message' => e.message }
  end
  
  def batch_process(texts, options = {})
    request_data = {
      texts: texts,
      exaggeration: options[:exaggeration] || 0.6,
      cfg_weight: options[:cfg_weight] || 0.5,
      temperature: options[:temperature] || 1.0,
      output_format: options[:output_format] || 'wav'  # NEW: Format support
    }
    
    batch_options = @options.merge(body: request_data.to_json, timeout: 120)
    response = self.class.post('/batch-tts', batch_options)
    
    if response.success?
      response.parsed_response
    else
      { 'success' => false, 'message' => "HTTP #{response.code}: #{response.body}" }
    end
  rescue => e
    { 'success' => false, 'message' => e.message }
  end
end

def run_examples
  puts "🎤 Chatterbox TTS API v3.0 - Ruby Examples"
  puts "=" * 60
  
  client = ChatterboxClient.new
  
  # 1. Health Check
  puts "\n🏥 Checking API Health"
  puts "-" * 50
  return unless client.check_health
  
  # 2. Queue Status Check (NEW in v3.0)
  puts "\n📊 Checking Queue Status"
  puts "-" * 50
  client.check_queue_status
  
  # 3. Basic TTS with job tracking
  puts "\n🎵 Basic TTS Example (v3.0 Enhanced)"
  puts "-" * 50
  
  text = "Hello! This is a demonstration of the enhanced Chatterbox TTS API version 3.0 using Ruby. Now with job tracking and multiple output formats!"
  puts "Generating speech for: \"#{text[0, 50]}...\""
  
  result = client.generate_speech(text, exaggeration: 0.7, output_format: 'wav')
  
  if result['success']
    puts "✅ Speech generated successfully!"
    puts "   Job ID: #{result['job_id'] || 'unknown'}"
    puts "   Duration: #{result['duration_seconds']}s"
    puts "   Sample Rate: #{result['sample_rate']}Hz"
    puts "   Base64 length: #{result['audio_base64']&.length || 0} characters"
    
    # Save to file
    if result['audio_base64']
      audio_data = Base64.decode64(result['audio_base64'])
      File.write('output_basic.wav', audio_data, mode: 'wb')
      puts "   Audio saved to: output_basic.wav"
    end
    
    # Test job status endpoint (NEW in v3.0)
    if result['job_id']
      puts "\n🔍 Testing job status endpoint..."
      job_status = client.check_job_status(result['job_id'])
      if job_status
        puts "   Job Status: #{job_status['status'] || 'unknown'}"
        puts "   Job Type: #{job_status['job_type'] || 'unknown'}"
      end
    end
  else
    puts "❌ Basic TTS failed: #{result['message']}"
  end
  
  # 4. Output Format Testing (NEW in v3.0)
  puts "\n🎵 Testing Different Output Formats"
  puts "-" * 50
  
  formats = ['wav', 'mp3', 'ogg']
  test_text = "Testing different audio formats: WAV, MP3, and OGG!"
  
  formats.each do |format|
    puts "\nGenerating #{format.upcase} format..."
    
    result = client.generate_speech(
      test_text,
      exaggeration: 0.6,
      output_format: format,
      return_base64: true
    )
    
    if result['success']
      audio_data = Base64.decode64(result['audio_base64'])
      filename = "output_format_test.#{format}"
      File.write(filename, audio_data, mode: 'wb')
      
      puts "✅ #{format.upcase} generated successfully!"
      puts "   Job ID: #{result['job_id'] || 'unknown'}"
      puts "   File: #{filename}"
      puts "   Size: #{File.size(filename)} bytes"
      puts "   Duration: #{result['duration_seconds']}s"
    else
      puts "❌ #{format.upcase} generation failed: #{result['message'] || 'Unknown error'}"
    end
  end
  
  # 3. Voice Cloning (if reference audio exists)
  puts "\n🎭 Voice Cloning Example"
  puts "-" * 50
  
  reference_audio = '../test_audio.wav'
  if File.exist?(reference_audio)
    puts "Cloning voice from: #{reference_audio}"
    
    result = client.voice_clone(
      "This is voice cloning in action using Ruby! I should sound like the reference audio.",
      reference_audio,
      exaggeration: 0.6
    )
    
    if result['success']
      puts "✅ Voice cloning successful!"
      
      if result['audio_base64']
        audio_data = Base64.decode64(result['audio_base64'])
        File.write('output_cloned.wav', audio_data, mode: 'wb')
        puts "   Cloned voice saved to: output_cloned.wav"
        puts "   Duration: #{result['duration_seconds']}s"
      elsif result['audio_data']
        File.write('output_cloned.wav', result['audio_data'], mode: 'wb')
        puts "   Cloned voice saved to: output_cloned.wav"
      end
    else
      puts "❌ Voice cloning failed: #{result['message']}"
    end
  else
    puts "❌ Reference audio not found: #{reference_audio}"
    puts "   Please provide a reference audio file to test voice cloning"
  end
  
  # 4. Batch Processing
  puts "\n📚 Batch Processing Example"
  puts "-" * 50
  
  texts = [
    "This is the first sentence in our Ruby batch processing demonstration.",
    "Here's the second sentence with different content and style.",
    "And finally, the third sentence completes our batch example.",
    "Bonus fourth sentence showing the power of batch processing!"
  ]
  
  puts "Processing batch of #{texts.length} texts..."
  
  result = client.batch_process(texts, exaggeration: 0.6)
  
  if result['success']
    puts "✅ Batch processing completed!"
    puts "   Total duration: #{result['total_duration']}s"
    puts "   Results:"
    
    result['results'].each_with_index do |item_result, index|
      if item_result['success']
        audio_data = Base64.decode64(item_result['audio_base64'])
        output_file = "output_batch_#{index + 1}.wav"
        File.write(output_file, audio_data, mode: 'wb')
        
        puts "     #{index + 1}. ✅ #{output_file} (#{item_result['duration_seconds']}s)"
      else
        puts "     #{index + 1}. ❌ Failed: #{item_result['message'] || 'Unknown error'}"
      end
    end
  else
    puts "❌ Batch processing failed: #{result['message']}"
  end
  
  # 5. Advanced Parameters Demo
  puts "\n🎛️ Advanced Parameters Demo"
  puts "-" * 50
  
  presets = [
    {
      name: 'Subtle & Calm',
      params: { exaggeration: 0.2, cfg_weight: 0.3, temperature: 0.8 },
      text: 'This is a calm and subtle voice with minimal emotion.'
    },
    {
      name: 'Expressive & Dynamic',
      params: { exaggeration: 1.2, cfg_weight: 0.8, temperature: 1.3 },
      text: 'This voice is very expressive and dynamic with lots of emotion!'
    },
    {
      name: 'Balanced & Natural',
      params: { exaggeration: 0.5, cfg_weight: 0.5, temperature: 1.0 },
      text: 'This is a balanced, natural-sounding voice setting.'
    }
  ]
  
  presets.each_with_index do |preset, index|
    puts "\nTesting: #{preset[:name]}"
    puts "Parameters: #{preset[:params]}"
    
    result = client.generate_speech(preset[:text], preset[:params].merge(return_base64: true))
    
    if result['success']
      audio_data = Base64.decode64(result['audio_base64'])
      file_name = preset[:name].downcase.gsub(/[^a-z0-9]/, '_')
      output_file = "output_preset_#{index + 1}_#{file_name}.wav"
      
      File.write(output_file, audio_data, mode: 'wb')
      puts "✅ Saved: #{output_file} (#{result['duration_seconds']}s)"
    else
      puts "❌ Failed: #{result['message'] || 'Unknown error'}"
    end
  end
  
  puts "\n" + "=" * 60
  puts "🎉 All examples completed!"
  puts "Check the generated audio files in the current directory."
end

# Run examples if called directly
if __FILE__ == $0
  begin
    run_examples
  rescue => e
    puts "❌ Unexpected error: #{e.message}"
    exit 1
  end
end
```

## Sinatra Web Integration

```ruby
require 'sinatra'
require 'json'

# Initialize TTS client
tts_client = ChatterboxClient.new

# Enable CORS
before do
  response.headers['Access-Control-Allow-Origin'] = '*'
  response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
  response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
end

# Handle preflight requests
options '*' do
  response.headers['Allow'] = 'GET, POST, OPTIONS'
  response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
  200
end

get '/' do
  erb :index
end

post '/generate' do
  content_type :json
  
  request_payload = JSON.parse(request.body.read)
  text = request_payload['text']
  
  if text.nil? || text.strip.empty?
    halt 400, { error: 'Text is required' }.to_json
  end
  
  result = tts_client.generate_speech(text, request_payload)
  
  if result['success']
    result.to_json
  else
    halt 500, { error: result['message'] }.to_json
  end
end

get '/health' do
  content_type :json
  
  is_healthy = tts_client.check_health
  { healthy: is_healthy }.to_json
end
```

## Running the Examples

```bash
# Install dependencies
gem install httparty base64

# Run CLI examples
ruby basic_usage.rb

# Run web server (requires sinatra gem)
gem install sinatra
ruby web_app.rb
```
